# list operations

# fast order preserving list uniquification function from:
# http://www.peterbe.com/plog/uniqifiers-benchmark
def uniquify(list, idfun=None): 
   '''
   removes duplicate items from a list
   '''
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in list:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result