def iterfact(n):
    print("Line 2: ",n)  
    assert n >= 0 and n % 1 == 0, "Positive integers only, please! " 
    if n == 0 or n == 1:
        #print("0 or 1, done")
        return 1
    ans = 1
    for i in range(1,n+1):
        ans = ans * i
    #print(ans)
    return(ans)


def fact1(n):
    if n == 1:
        return 1
    else:
        return(fact1(n-1)*n)

def recfact_v1(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n == 1: 
        return 1
    if n == 0: 
        return 1
    return(n*recfact_v1(n-1))

def recfact_or0(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n == 0 or n ==1:
        return 1
    return(n*recfact_or0(n-1))

def recfact_or1(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n == 1 or n ==0:
        return 1
    return(n*recfact_or1(n-1))

def recfact_one(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n <= 1:
        return 1
    return(n*recfact_one(n-1))

def recfact_lt(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n < 2:
        return 1
    return(n*recfact_lt(n-1))


def recfact_one(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n <= 1:
        return 1
    return(n*recfact_one(n-1))

def recfact_lt(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n < 2:
        return 1
    return(n*recfact_lt(n-1))
    
def recfact_set(n):
    assert n >= 0 and int(n) == n, "positive integers only, please! :-) "
    if n in [0,1]:
        return 1
    return(n*recfact_set(n-1))
