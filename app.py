import json
import os
import streamlit as st
from mix_design_tool import calculate_mix_design, EXPOSURE_RULES
from purchase_planner import calculate_purchase_plan, purchase_csv, explain_plan, MATERIALS
from agent import run_agent

st.set_page_config(page_title='ConcreteAI SitePlan', page_icon='🏗️', layout='wide')
st.markdown('### CONCRETEAI / SITEPLAN')
st.title('Know what to buy. Know the cost.')
st.caption('Concrete material planning • Stock-aware purchases • English / Urdu / Roman Urdu')
st.info('Final hackathon upgrade: turn a preliminary mix estimate into a costed material purchase plan.')


def setting(name, default=''):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


def number_input(container, label, minimum, maximum, default, step=None, *, key, disabled=False):
    if key not in st.session_state:
        st.session_state[key] = default
    return container.number_input(label, min_value=minimum, max_value=maximum, value=None,
                                  step=step, key=key, disabled=disabled)


def load_demo():
    values = dict(project='Demo — 20 × 15 ft roof', length=20., width=15., thickness=6.,
                  allowance=5., bag=50., sand_density=1600., agg_density=1500.,
                  mix_mode='Educational mix estimate', strength=3000, exposure='mild',
                  stock_cement=12., stock_sand=30., stock_aggregate=50., stock_water=0.,
                  rate_cement=1400., rate_sand=80., rate_aggregate=140., rate_water=1.,
                  delivery=2500., use_budget=True, budget=50000.)
    for key in ['cement','sand','aggregate','water']:
        values['known_'+key] = True
    st.session_state.update(values)
    st.session_state.pop('agent_result', None)


with st.sidebar:
    st.header('Project settings')
    language = st.selectbox('Explanation language', ['English','Urdu (اردو)','Roman Urdu'])
    st.button('Load demo project', on_click=load_demo, width='stretch')
    st.caption('Demo prices and densities are illustrative, not market quotes or lab measurements.')
    st.session_state.setdefault('project', 'My concrete project')
    project = st.text_input('Project name', value=None, key='project')
    mix_mode = st.radio('Mix source', ['Educational mix estimate','Enter project mix (kg/m³)'], key='mix_mode')
    if mix_mode == 'Educational mix estimate':
        strength = number_input(st, 'Requested strength (psi)', 2000, 5000, 3000, 500, key='strength')
        exposure = st.selectbox('Demo exposure preset', list(EXPOSURE_RULES), key='exposure')
        st.caption('Inherited demo presets only. They do not establish an ACI exposure class or certify strength.')
        if strength is None:
            st.error('Enter a requested strength to continue.')
            st.stop()
        mix = calculate_mix_design(strength, exposure)
    else:
        st.caption('Enter an engineer/lab-provided mix. The app does not validate its suitability.')
        cement = number_input(st, 'Cement kg/m³', 1., 1000., 350., key='mix_cement')
        sand = number_input(st, 'Sand kg/m³', 1., 2000., 750., key='mix_sand')
        agg = number_input(st, 'Coarse aggregate kg/m³', 1., 2500., 1050., key='mix_agg')
        water = number_input(st, 'Water kg/m³', 1., 500., 180., key='mix_water')
        if any(v is None for v in (cement, sand, agg, water)):
            st.error('Complete all four mix quantities to continue.')
            st.stop()
        mix = dict(cement_kg_m3=cement, sand_kg_m3=sand, coarse_agg_kg_m3=agg, water_kg_m3=water,
                   basis='User-supplied project mix; suitability not checked',
                   warnings=['User-supplied mix is not validated by this application. Engineering review is required.'])
    with st.expander('AI connection (optional)'):
        model = st.text_input('Anthropic model', value=setting('ANTHROPIC_MODEL','claude-haiku-4-5-20251001'))
        key_input = st.text_input('API key for this session', type='password')
        api_key = key_input or setting('ANTHROPIC_API_KEY')
        st.caption('An API key is needed only for live Claude. Keep it out of GitHub. Only click Run live agent to send the current project inputs to Anthropic.')
    st.caption('Prototype • Preliminary estimates • Lab trials and engineering review required')

planner_tab, mix_tab, agent_tab = st.tabs(['01  Cost & purchase plan','02  Mix & assumptions','03  AI assistant'])
with planner_tab:
    st.subheader('1. Size the concrete work')
    cols = st.columns(4)
    length = number_input(cols[0], 'Length (ft)', 0., 1000., 20., .5, key='length')
    width = number_input(cols[1], 'Width (ft)', 0., 1000., 15., .5, key='width')
    thickness = number_input(cols[2], 'Thickness (inches)', 0., 120., 6., .5, key='thickness')
    allowance = number_input(cols[3], 'Quantity allowance (%)', 0., 30., 5., 1., key='allowance')
    st.caption('Thickness is in inches. This rectangular estimate excludes beams, openings and irregular shapes; adjust the scope separately.')
    with st.expander('Bag size and purchasing density assumptions', expanded=False):
        cols = st.columns(3)
        bag = number_input(cols[0], 'Cement bag weight (kg)', 1., 100., 50., key='bag')
        sand_density = number_input(cols[1], 'Sand bulk density (kg/m³)', 500., 2500., 1600., key='sand_density')
        agg_density = number_input(cols[2], 'Aggregate bulk density (kg/m³)', 500., 2500., 1500., key='agg_density')
        st.caption('Default bulk densities are illustrative. Replace them with supplier/measured values consistent with the purchased material. Sand bulking and moisture can change bulk volume.')
    st.subheader('2. Enter stock and local prices')
    st.caption('Check “Price entered” only when the rate is known. Zero is accepted as an explicitly free supply. Cement stock and prices use the selected bag weight.')
    stock, rates = {}, {}
    for key, label, unit in MATERIALS:
        cols = st.columns([1.4,2,2,1.4])
        cols[0].markdown(f'**{label}**\n\n{unit}')
        stock[key] = number_input(cols[1], f'{label} available ({unit})', 0., None, 0., key='stock_'+key)
        rate = number_input(cols[2], f'{label} rate (PKR/{unit})', 0., None, 0., key='rate_'+key)
        known = cols[3].checkbox('Price entered', key='known_'+key)
        rates[key] = rate if known else None
    cols = st.columns(3)
    delivery = number_input(cols[0], 'Remaining delivery charges (PKR)', 0., None, 0., key='delivery')
    use_budget = cols[1].checkbox('Compare remaining purchases with a budget', key='use_budget')
    budget_input = number_input(cols[2], 'Remaining purchase budget (PKR)', 0., None, 50000., key='budget', disabled=not use_budget)
    budget = budget_input if use_budget else None
    inputs = dict(mix=mix, length_ft=length, width_ft=width, thickness_in=thickness,
                  allowance_pct=allowance, bag_weight_kg=bag, sand_bulk_kg_m3=sand_density,
                  aggregate_bulk_kg_m3=agg_density, stock=stock, rates=rates,
                  delivery_pkr=delivery, budget_pkr=budget, project=project)
    plan = None
    try:
        plan = calculate_purchase_plan(**inputs)
    except ValueError as error:
        st.error(str(error))
    if plan:
        st.divider()
        st.subheader('3. Your purchase plan')
        cols = st.columns(4)
        cols[0].metric('Net concrete volume', f"{plan['volume_cft']:,.1f} cft")
        cols[1].metric('Including allowance', f"{plan['planned_volume_m3']:,.2f} m³")
        total = plan['purchase_total_pkr']
        cols[2].metric('Remaining purchases + delivery', 'Prices needed' if total is None else f'PKR {total:,.0f}')
        balance = plan['budget_balance_pkr']
        cols[3].metric('Budget shortfall' if balance is not None and balance < 0 else 'Budget remaining',
                       'Not assessed' if balance is None else f'PKR {abs(balance):,.0f}')
        if plan['missing_purchase_prices']:
            st.warning('Incomplete estimate. Enter prices for: ' + ', '.join(plan['missing_purchase_prices']))
        elif balance is not None and balance < 0:
            st.error('Over budget. Review supplier quotes, available stock and delivery costs. Keep the specified mix and strength.')
        elif balance is not None:
            st.success('Within the entered remaining-purchase budget for the listed items.')
        rows = [{'Material':r['material'],'Unit':r['unit'],'Required':round(r['required'],2),
                 'Available':round(r['stock'],2),'Buy':round(r['purchase'],2),
                 'PKR / unit':'Not entered' if r['rate_pkr'] is None else f"{r['rate_pkr']:,.2f}",
                 'Purchase PKR':'Incomplete' if r['cost_pkr'] is None else f"{r['cost_pkr']:,.2f}"}
                for r in plan['rows']]
        st.dataframe(rows, hide_index=True, width='stretch')
        st.caption('Cement purchases are rounded up to whole bags after subtracting stock. Other quantities are displayed to 2 decimals; calculations use full precision.')
        material_value = plan['material_value_pkr']
        st.caption('Full material value, including stock, excluding delivery and purchase rounding: ' +
                   ('enter all material rates to calculate.' if material_value is None else f'PKR {material_value:,.0f}.'))
        st.info(explain_plan(plan, language))
        st.download_button('Download purchase list (.csv)', purchase_csv(plan), 'ConcreteAI-Purchase-List.csv', 'text/csv', type='primary')
        st.caption('Materials and entered delivery only. Labour, equipment, taxes and unentered charges are excluded.')
        with st.expander('Calculation details and assumptions'):
            st.code('Concrete cft = length ft × width ft × thickness inches ÷ 12\nBulk material cft = material mass kg ÷ bulk density kg/m³ × 35.3146667\nBuy = max(0, required − stock); round cement purchases up to whole bags\nPurchase cost = buy × entered unit rate\nBudget balance = remaining purchase budget − (purchase costs + delivery)')
            st.json(plan)

with mix_tab:
    st.subheader('Mix quantities per cubic metre')
    cols = st.columns(4)
    for col, (label, key) in zip(cols, [('Cement','cement_kg_m3'),('Sand','sand_kg_m3'),('Coarse aggregate','coarse_agg_kg_m3'),('Water','water_kg_m3')]):
        col.metric(label, f"{mix[key]:,.1f} {'L' if key == 'water_kg_m3' else 'kg'}")
    if 'wc_ratio' in mix:
        st.caption(f"Demo calculation basis: {mix['final_psi']:g} psi · w/c {mix['wc_ratio']:.3f}. Calculated proportions do not guarantee strength.")
    for warning in mix['warnings']:
        st.warning(warning)
    st.write('The educational engine uses a fixed water estimate, 2% air, assumed specific gravities, and a fixed coarse aggregate factor. The strength–water/cement table is an inherited demo approximation with interpolation. The strength range is limited to 2000–5000 psi.')
    st.write('Purchasing cft uses bulk density. It must not be used as a field batching ratio. No moisture correction, reinforcement design, achieved-strength prediction, or code-compliance certification is provided.')
    st.json(mix)

with agent_tab:
    st.subheader('Ask about the current project')
    st.write('Fill the planner first. The assistant can call Python tools to read the mix and calculate the purchase plan. Change dimensions, prices or stock in the form before asking about a new scenario.')
    prompt = st.text_area('Your question', value='Explain what I still need to buy and whether my remaining budget is enough.')
    fingerprint = json.dumps({'inputs':inputs,'language':language,'question':prompt,'model':model}, sort_keys=True)
    cols = st.columns(2)
    live = cols[0].button('Run live agent', disabled=not api_key or plan is None, type='primary')
    offline = cols[1].button('Show offline plan summary', disabled=plan is None)
    if not api_key:
        st.caption('No API key configured. Offline calculation and downloads work without an LLM.')
    if live and prompt.strip():
        with st.spinner('Claude is deciding which calculation tools to call…'):
            try:
                result = run_agent(prompt, language, inputs,
                                   lambda:calculate_mix_design(strength, exposure) if mix_mode == 'Educational mix estimate' else mix,
                                   lambda:calculate_purchase_plan(**inputs), api_key, model)
            except Exception as error:
                result = {'answer':explain_plan(plan,language), 'trace':[],
                          'mode':f'API unavailable ({type(error).__name__}); deterministic offline summary — not an AI answer'}
        st.session_state.agent_result = {'fingerprint':fingerprint, **result}
    if offline:
        st.session_state.agent_result = {'fingerprint':fingerprint,'answer':explain_plan(plan,language),
                                        'trace':[], 'mode':'Offline deterministic summary — does not interpret the question'}
    saved = st.session_state.get('agent_result')
    if saved:
        if saved['fingerprint'] != fingerprint:
            st.warning('Project inputs or question changed. Run the assistant again to refresh its answer.')
        else:
            st.caption(saved['mode'])
            st.write(saved['answer'])
            if saved['trace']:
                with st.expander('Actual tool calls', expanded=True):
                    for event in saved['trace']:
                        st.markdown('**' + event['tool'] + '()**')
                        st.json(event)

st.divider()
st.caption('ConcreteAI SitePlan • PakAngel Cohort C11 • Preliminary planning prototype. Validate mix and material properties before construction.')
