from metadata import REQUEST_STATE


##Test ##   
ll  = list(REQUEST_STATE)    
print(len(ll))
print(ll)
dd =[c.value for c in REQUEST_STATE]
print(dd)
ww= REQUEST_STATE.COMPLETED_HEALTH
print(type(REQUEST_STATE.COMPLETED_HEALTH.value))
if (ww == REQUEST_STATE.COMPLETED_HEALTH):
    print("True")
else:
    print("False")
