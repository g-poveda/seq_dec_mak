def exercise_model(N=20):
    model = cp_model.CpModel()
    df = pd.Series(range(N))
    X = model.NewBoolVarSeries("X", df.index)
    Y = model.NewBoolVarSeries("Y", df.index[:-1])
    # Auxiliary variable, Y_prime[i]==1 <-> X[i]==X[i+1] (if and only if) 
    Y_prime = model.NewBoolVarSeries("Y_prime", df.index[:-1])
    Z = model.NewIntVar(lb=0, ub=2*N, name="Z")
    for i in range(N-1):
        # Here we set equivalence between Y_prime[i] and (X[i]==X[i+1])
        model.Add(X[i]==X[i+1]).OnlyEnforceIf(Y_prime[i])
        model.Add(X[i]!=X[i+1]).OnlyEnforceIf(Y_prime[i].Not())
        # if X[i]==X[i+1] then Y[i]==True, which is what we wanted !! 
        model.Add(Y[i]==True).OnlyEnforceIf(Y_prime[i])
    for i in range(N-3):
        model.Add(Y[i]!=Y[i+2])
    model.Add(sum(X[::3])+sum(Y)==Z)
    model.Maximize(Z)
    return model, X, Y, Z
