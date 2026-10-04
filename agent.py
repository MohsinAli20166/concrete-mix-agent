"""Claude tool-use over a confirmed form snapshot. No model-generated arithmetic."""
import json

TOOLS = [
    {'name':'calculate_mix_design', 'description':'Return the mix calculated from the current confirmed form inputs. Does not certify strength or code compliance.',
     'input_schema':{'type':'object','properties':{},'additionalProperties':False}},
    {'name':'calculate_purchase_plan', 'description':'Calculate quantities, remaining purchases, entered-price costs and budget status using the current form snapshot.',
     'input_schema':{'type':'object','properties':{},'additionalProperties':False}},
]


def run_agent(question, language, context, mix_fn, plan_fn, api_key, model, client=None):
    if client is None:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key, timeout=30., max_retries=0)
    system = (
        'You are ConcreteAI SitePlan, a preliminary material purchase assistant. '
        'Use the tools for ALL numerical results; never invent prices, quantities or code requirements. '
        'Tools use the current user-confirmed form only. If the question changes a value, asks for missing data, '
        'or conflicts with the form, ask the user to update the form and rerun; do not silently use old values. '
        'Call calculate_mix_design for mix questions and calculate_purchase_plan for purchase/cost/budget questions. '
        'The presets are educational, not verified ACI exposure classifications. Do not claim an achieved strength '
        'or code compliance. Never recommend reducing specified strength to save cost. '
        'Missing rates make totals incomplete, not zero. Distinguish full material value from remaining purchases. '
        f'Respond in {language}. Current confirmed form snapshot: ' + json.dumps(context, ensure_ascii=False)
    )
    messages = [{'role':'user','content':question}]
    trace = []
    for _ in range(5):
        response = client.messages.create(model=model, max_tokens=1400, system=system,
                                          tools=TOOLS, messages=messages)
        calls = [b for b in response.content if b.type == 'tool_use']
        if not calls:
            answer = '\n'.join(b.text for b in response.content if b.type == 'text')
            return {'answer':answer or 'Please update the form and try again.', 'trace':trace,
                    'mode':'Live Claude tool-use' if trace else 'Live Claude clarification (no tool call)'}
        messages.append({'role':'assistant','content':response.content})
        results = []
        for call in calls:
            failed = False
            try:
                if call.input:
                    raise ValueError('Tools accept no overrides. Ask the user to update the form.')
                if call.name == 'calculate_mix_design':
                    output = mix_fn()
                elif call.name == 'calculate_purchase_plan':
                    output = plan_fn()
                else:
                    raise ValueError('Unknown tool')
            except (ValueError, TypeError, KeyError) as error:
                failed, output = True, {'error':str(error)}
            trace.append({'tool':call.name, 'input':call.input, 'output':output, 'is_error':failed})
            results.append({'type':'tool_result','tool_use_id':call.id,
                            'content':json.dumps(output, ensure_ascii=False),'is_error':failed})
        messages.append({'role':'user','content':results})
    return {'answer':'Tool-call limit reached. Use the verified planner results below.',
            'trace':trace, 'mode':'Live agent stopped at tool-call limit'}
