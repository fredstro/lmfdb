r"""

Utility functions for the subgroups. 

"""

from lmfdb.psl2z_subgroups.backend.psg_schema import PSL2Zsubgroup,Signature_class

def is_consistent_signature(signature):
    r"""
    Check if a given siganature is (mathematically) consistent.
    """
    
    index = signature.get('index',None)
    nu = signature.get('nu',None)
    e2 = signature.get('e2',None)
    e3 = signature.get('e3',None)
    g = signature.get('g',None)
    if index == None: ## simple check
        if nu == None or e2 == None or e3 == None or g == None:
            return True
        if 12*g - 12 + 6*nu + 3*e2 + 4*e3 >0:
            return True
        return False
    elif index < 1:
        return False
    if nu <> None and e2 <> None and e3 <> None and g <> None:    
        return 12*g - 12 + 6*nu + 3*e2 + 4*e3 >0
    # else we need to check for solutions to the above inequality
    if nu <> None:
        hrange = [nu]
    else:
        hrange = range(1,index+1)
    if e2 <> None:
        e2range = [e2]
    else:
        e2range = range(0, int( (12+index)/3) +1)
    if e3 <> None:
        e3range = [e3]
    else:
        e3range = range(0, int( (12+index)/3) +1)        
    for h in hrange:
        for e2 in e2range:
            if 3*e2 > 12 + index - 6*h:
                continue
            for e3 in e3range:
                if 4*e3 > 12 + index - 6*h - 3*e2:
                    continue
                genus12=12+index-6*h-3*e2-4*e3                
                if genus12 < 0 or (g<>None and 12*g<>genus12):
                    continue
                if genus12 % 12 == 0: # we have a valid type
                    return True
    return False


def get_signature(request,**kwds):
    names = ['index','nu','e2','e3','g']
    res = {}
    for x in names:
        val = request.args.get(x,kwds.get(x,None))
        if val <> None:
            res[x]=val
    return res

def build_signature_query(signature):
    r"""
    Take a signature in form of a dict and build a query object.
    """
    q = Signature_class.query
    index = signature.get('index',None)
    nu = signature.get('nu',None)
    e2 = signature.get('e2',None)
    e3 = signature.get('e3',None)
    g = signature.get('g',None)
    if index <> None and index>0:
        q = q.filter_by(psl2z_index=int(index))
    if nu <> None:
        q = q.filter_by(nu=int(nu))
    if e2 <> None:
        q = q.filter_by(e2=int(e2))
    if e3 <> None:
        q = q.filter_by(e3=int(e3))
    if g <> None:
        q = q.filter_by(g=int(g))
    return q


def render_plot(g,type=0):
    r"""
    Takes an instance of PSL2Zsubgroups and returns a plot frm the database
    """
    p2 = permutation_to_compact_string(g.p3,g.psl2z_index)
    p3 = permutation_to_compact_string(g.p3,g.psl2z_index)
    s = g.signature_as_string()
    filename = 'domain-{0}-{1}-{2}.png'.format(s,p2,p3)
    C = lmfdb.base.getDBConnection()
    res = C['SL2Zsubgroups']['groups2'].find_one({'filename':filename})
    if res==None:
        return None
    elif type == 0:
        return res['domain']
    else:
        return res['domain_farey']



def permutation_to_compact_string(entries,N,sep='0'):
    r"""
    Export a permutation in format '(1 2 3)' to a compact string without spaces, '231' (in this case).
    """
    if not isinstance(entries,list):
        entries = permutation_to_list(entries)
    s=''
    base=N+1
    # We don't want to use alphanumeric characters as separators except for 0
    if sep.isalnum() and sep<>'0':
        raise ValueError,"Need a non-alphanumeric separator! Got {0}".format(sep)
    if base<=36 and (sep=='0' or sep==""):
        for i in range(N):
            s+=Integer(entries[i]).str(base)
    else: # If we have more than one symbol per char we insert zeros instead
        for i in range(N-1):
            s+=str(entries[i])+sep
        s+=str(entries[N-1])
    if sep<>"0" and sep<>"":
        s+=".{0}".format(sep)  ## If not "0" we give the separator explicitly
    return s
