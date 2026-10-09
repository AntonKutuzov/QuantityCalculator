from QCalculator import Formula, Datum


unit_dict = {
    'w_mV': 'mg/L',
    'm': 'mg',
    'V_mix': 'mL',
    ('C', 'C_stock'): 'ug/mL',
    ('V', 'V_stock'): 'mL'
}

w_mV = Formula('w_mV = m/V_mix', def_units=unit_dict)
w_mV.write(
    'm = 1.249 g',
    'V_mix = 1 L'
)

w_CaCO3 = w_mV.solve(units='mg/L')[0]
w_Ca = w_CaCO3.scale(40/100)  # mass fraction of Ca in CaCO3


dilutor = Formula('C_stock * V_stock = C * V', def_units=unit_dict)
dilutor.write('V = 5 mL', f'C_stock = {w_Ca.quantity}')
dilutor.target = 'V_stock = 0.0001 mL'

concs = [0, 1, 2, 3, 4, 5]

for c in concs:
    dilutor.write(f'C = {c} ug/mL', rewrite=True)
    res = dilutor.solve(units='uL', round_to=0)[0]
    print(res)
