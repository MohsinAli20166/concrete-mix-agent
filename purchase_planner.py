"""Pure arithmetic for material stock, bulk purchase quantities and PKR costs."""
import csv
import io
import math
from mix_design_tool import M3_TO_CFT, number

MATERIALS = [('cement', 'Cement', 'bags'), ('sand', 'Sand', 'cft'),
             ('aggregate', 'Coarse aggregate', 'cft'), ('water', 'Water', 'L')]


def calculate_purchase_plan(mix, length_ft, width_ft, thickness_in, allowance_pct,
                            bag_weight_kg, sand_bulk_kg_m3, aggregate_bulk_kg_m3,
                            stock, rates, delivery_pkr=0, budget_pkr=None, project='My project'):
    length = number(length_ft, 'Length', .01)
    width = number(width_ft, 'Width', .01)
    thickness = number(thickness_in, 'Thickness', .01)
    allowance = number(allowance_pct, 'Allowance', 0, 30)
    bag = number(bag_weight_kg, 'Bag weight', 1, 100)
    sand_density = number(sand_bulk_kg_m3, 'Sand bulk density', 500, 2500)
    aggregate_density = number(aggregate_bulk_kg_m3, 'Aggregate bulk density', 500, 2500)
    cement = number(mix.get('cement_kg_m3'), 'Cement kg/m3', .01)
    sand = number(mix.get('sand_kg_m3'), 'Sand kg/m3', .01)
    aggregate = number(mix.get('coarse_agg_kg_m3'), 'Aggregate kg/m3', .01)
    water = number(mix.get('water_kg_m3'), 'Water kg/m3', .01)
    volume_cft = length * width * thickness / 12
    volume_m3 = volume_cft / M3_TO_CFT
    order_volume = volume_m3 * (1 + allowance/100)
    required = dict(cement=cement*order_volume/bag,
                    sand=sand*order_volume/sand_density*M3_TO_CFT,
                    aggregate=aggregate*order_volume/aggregate_density*M3_TO_CFT,
                    water=water*order_volume)
    delivery = number(delivery_pkr, 'Delivery', 0)
    budget = None if budget_pkr is None else number(budget_pkr, 'Budget', 0)
    rows, missing_purchase, missing_value = [], [], []
    purchase_subtotal, material_value = 0., 0.
    for key, label, unit in MATERIALS:
        available = number(stock.get(key, 0), f'{label} stock', 0)
        deficit = max(0., required[key] - available)
        # Tolerance avoids a floating-point dust shortage becoming a full bag.
        purchase = math.ceil(deficit-1e-10) if key == 'cement' else deficit
        rate = None if rates.get(key) is None else number(rates[key], f'{label} rate', 0)
        cost = 0. if purchase == 0 else (None if rate is None else purchase*rate)
        value = None if rate is None else required[key]*rate
        if cost is None:
            missing_purchase.append(label)
        else:
            purchase_subtotal += cost
        if value is None:
            missing_value.append(label)
        else:
            material_value += value
        rows.append(dict(material=label, key=key, unit=unit, required=required[key],
                         stock=available, purchase=purchase, rate_pkr=rate, cost_pkr=cost,
                         remaining_stock=max(0., available+purchase-required[key])))
    total = None if missing_purchase else purchase_subtotal + delivery
    balance = None if total is None or budget is None else budget-total
    status = ('incomplete_prices' if total is None else 'no_budget' if budget is None
              else 'over_budget' if balance < 0 else 'within_budget')
    return dict(project=str(project), volume_cft=volume_cft, volume_m3=volume_m3,
                planned_volume_m3=order_volume, allowance_pct=allowance, rows=rows,
                known_purchase_subtotal_pkr=purchase_subtotal, delivery_pkr=delivery,
                purchase_total_pkr=total, material_value_pkr=None if missing_value else material_value,
                missing_purchase_prices=missing_purchase, budget_pkr=budget,
                budget_balance_pkr=balance, budget_status=status,
                assumptions={'bag_weight_kg':bag, 'sand_bulk_kg_m3':sand_density,
                             'aggregate_bulk_kg_m3':aggregate_density, 'mix_basis':mix.get('basis', 'User-supplied mix'),
                             'mix_kg_per_m3': {'cement':cement, 'sand':sand, 'aggregate':aggregate, 'water':water}},
                warnings=list(mix.get('warnings', [])) + [
                    'Prices are user-entered. Labour, equipment, taxes and other unentered charges are excluded.',
                    'Bulk cft are purchasing estimates using entered bulk densities; solid volume is not loose purchase volume.',
                    'Allowance increases total estimated quantity; it does not alter the mixture proportions.',
                    'Water is a planning quantity, not a site dosing instruction; moisture corrections are not calculated.'])


def _safe_csv(value):
    # Neutralize spreadsheet formulas in user-supplied project text.
    if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
        return "'" + value
    return value


def purchase_csv(plan):
    out = io.StringIO(newline='')
    writer = csv.writer(out)
    def row(*values):
        writer.writerow([_safe_csv(v) for v in values])
    row('ConcreteAI SitePlan — preliminary purchase estimate')
    row('Project', plan['project'])
    row('Net concrete volume m3', round(plan['volume_m3'], 4))
    row('Allowance percent', plan['allowance_pct'])
    row('Planned concrete volume m3', round(plan['planned_volume_m3'], 4))
    row('Material', 'Unit', 'Required incl allowance', 'Stock', 'Purchase', 'PKR per unit', 'Purchase cost PKR')
    for r in plan['rows']:
        row(r['material'], r['unit'], round(r['required'], 3), r['stock'], round(r['purchase'], 3),
            'NOT ENTERED' if r['rate_pkr'] is None else r['rate_pkr'],
            'INCOMPLETE' if r['cost_pkr'] is None else round(r['cost_pkr'], 2))
    for label, key in [('Delivery PKR','delivery_pkr'), ('Remaining purchase total PKR','purchase_total_pkr'),
                       ('Material value incl existing stock PKR','material_value_pkr'),
                       ('Remaining purchase budget PKR','budget_pkr'), ('Budget balance PKR','budget_balance_pkr')]:
        row(label, 'NOT AVAILABLE' if plan[key] is None else round(plan[key], 2))
    row('Budget status', plan['budget_status'])
    for key, value in plan['assumptions'].items():
        row(key, str(value))
    for warning in plan['warnings']:
        row('Note', warning)
    return out.getvalue().encode('utf-8-sig')


def explain_plan(plan, language='English'):
    if plan['purchase_total_pkr'] is None:
        missing = ', '.join(plan['missing_purchase_prices'])
        return {'English':f'Enter prices for {missing} before assessing the remaining purchase budget.',
                'Roman Urdu':f'{missing} ki qeemat darj karein. Is ke baghair budget ka mukammal hisaab nahin ho sakta.',
                'Urdu (اردو)':f'پہلے ان مواد کی قیمت درج کریں: {missing}۔ اس کے بغیر بجٹ کا مکمل حساب ممکن نہیں۔'}[language]
    total = f"PKR {plan['purchase_total_pkr']:,.0f}"
    purchase = '; '.join(f"{r['material']}: {r['purchase']:,.2f} {r['unit']}" for r in plan['rows'])
    balance = plan['budget_balance_pkr']
    if language == 'Roman Urdu':
        msg = f'Baqi khareedari aur delivery ka andazati kharcha {total} hai. Khareedna hai: {purchase}.'
        if balance is not None:
            msg += f" Budget {'kam hai' if balance < 0 else 'mein bachat hai'}: PKR {abs(balance):,.0f}."
        return msg + ' Yeh ibtidai takhmeena hai. Budget ke liye concrete ki specified strength kam na karein.'
    if language == 'Urdu (اردو)':
        msg = f'باقی خریداری اور ترسیل کا تخمینہ {total} ہے۔ خریدنے کی مقدار: {purchase}۔'
        if balance is not None:
            msg += f" بجٹ میں {'کمی' if balance < 0 else 'بچت'}: PKR {abs(balance):,.0f}۔"
        return msg + ' یہ ابتدائی تخمینہ ہے۔ بجٹ کی وجہ سے کنکریٹ کی مقررہ طاقت کم نہ کریں۔'
    msg = f'Remaining purchases plus delivery are estimated at {total}. Buy: {purchase}.'
    if balance is not None:
        msg += f" Budget {'shortfall' if balance < 0 else 'remaining'}: PKR {abs(balance):,.0f}."
    return msg + ' Keep the specified concrete strength. This is a preliminary estimate.'
