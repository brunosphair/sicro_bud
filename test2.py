import breakwater as bw

Hs = 3.35
Delta = 1.585
P = 0.5
Sd = 2
N = 1690
xi_m = 5.81
alpha = 0.588
Kd = 3.5

Dn50Hudson = bw.core.stability.hudson(Hs, Kd, Delta, alpha)
print('Hudson Dn50 = ', Dn50Hudson)

Dn50 = bw.core.stability.vandermeer_deep(Hs, Delta, P, Sd, N, xi_m, alpha)
print('Van der Meer Dn50 = ', Dn50)




Rc = bw.core.overtopping.rubble_mound(3.35, 2, 6.3933, 0.588, 0, 1, 1, 1, 'Rock', 2)

print('Rc = ',Rc)

#Dn50 = bw.core.stability.vandermeer_deep(3.24, 1.576, 0.5, 2, 3267, 3.06, 0.588)

#print('Dn50 = ', Dn50)