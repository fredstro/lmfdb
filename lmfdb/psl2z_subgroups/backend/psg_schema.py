from sage.all import PermutationGroupElement,matrix,ZZ
from sqlalchemy.ext.associationproxy import association_proxy

from lmfdb.psl2z_subgroups import db

Column = db.Column


class Conjugacy_class_psl(db.Model):
    r"""
    Class representing PSL(2,Z)-conjugacy classes of subgroups.
    """
    __tablename__ = 'Conjugacy_class_psl'
    id = db.Column(db.Integer, primary_key=True)
    representative = db.relationship('PSL2Zsubgroup')
    representative_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'),unique=True)
    #uix = db.UniqueConstraint('representative_id')

    _psl_conjugates = db.relationship('Conjugacy_class_elt',backref='conjugacy_class_psl',
                                      primaryjoin="Conjugacy_class_elt.conjugacy_class_psl_id==Conjugacy_class_psl.id")
    psl_conjugates = association_proxy('_psl_conjugates','group',
                                       creator = lambda (G,m): Conjugacy_class_elt(group=G,map_matrix=m))


    signature_id = db.Column(db.Integer,db.ForeignKey('Signature_class.id'))
    _signature = db.relationship('Signature_class',backref='conjugacy_classes_mod_psl',uselist=True)
    signature = association_proxy('_signature','name',
                                  creator = lambda (ix,nu,e2,e3,g):Signature(ix=int(ix),nu=int(nu),e2=int(e2),e3=int(e3),g=int(g)))

                                  
    def __repr__(self):
        return "List of {0} conjugates of {1}".format(len(self.psl_conjugates),self.representative)
    def length(self):
        return len(self.psl_conjugates)
    def __len__(self):
        return len(self.psl_conjugates)
    def __getitem__(self,i):
        return self.psl_conjugates.__getitem__(i)

    def __getslice__(self,i,j):
        return self.psl_conjugates.__getslice__(i,j)

    def __iter__(self):
        return self.psl_conjugates.__iter__()

    

class Conjugacy_class_elt(db.Model):
    r"""
    Element of a conjugacy class. Contains a group and a map taking it to the representative.
    """
    id =  db.Column('id', db.Integer, primary_key=True)
    conjugacy_class_psl_id= db.Column(db.Integer, db.ForeignKey('Conjugacy_class_psl.id'))
    group_id= db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    group = db.relationship('PSL2Zsubgroup',
                            primaryjoin = "Conjugacy_class_elt.group_id == PSL2Zsubgroup.id",
                            backref = db.backref("conjugacy_class_elt"))
    map_matrix = db.Column(db.UnicodeText)
    def __repr__(self):
        return '{0} conjugate by {1}'.format(self.group.__repr__(),self.map_matrix)


## Table describing the sub/supergroup relationships
## 
        
SubgroupRelationship = db.Table(
    'SubgroupRelationship', db.metadata,
    db.Column('supergroup_id', db.Integer, db.ForeignKey('PSL2Zsubgroup.id')),
    db.Column('subgroup_id', db.Integer, db.ForeignKey('PSL2Zsubgroup.id')),
    db.UniqueConstraint('supergroup_id', 'subgroup_id', name='uix_1')
    )

class PSL2Zsubgroup(db.Model):
    r"""
    Class for representing a subgroup of the modular group.
    Recall that a subgroup has a signature given by
    - index -- the index of self as a subgroup of the modular group
    - genus -- the genus of self
    - e2 -- the number of elliptic classes of order 2
    - e3 -- the number of elliptic classes of order 3
    - nu -- the number of cusp classes
    To uniquely describe the group we use the associated permutation representation.
    I.e. self is the group given by the conjugacy class of the pair (pS,pR) (conjugacy wrt. permutations fixing 1). See documentation elsewhere...

    """
    __tablename__ = 'PSL2Zsubgroup'
    id = db.Column('id', db.Integer, primary_key=True)
    ## Use the signature as primary keys
    psl2z_index = db.Column(db.Integer)  ## the name 'index' seems to cause trouble
    genus = db.Column(db.Integer)
    e2 = db.Column(db.Integer)
    e3 = db.Column(db.Integer)
    nu  = db.Column(db.Integer)
    # Coset representatives
    _coset_reps = db.relationship('Coset_rep_class',backref=db.backref('group'))
    coset_reps = association_proxy('_coset_reps','st',creator = lambda (a,b,c,d) : Coset_rep_class(a,b,c,d)) 
    # Generators
    _generators = db.relationship('Generator_class',backref=db.backref('group'))
    generators = association_proxy('_generators','st',creator = lambda (a,b,c,d) : Generator_class(a,b,c,d))
    
    label = db.Column(db.Unicode(100))  ## Automatically generated label for referencing (does this make sense to use?)
    name = db.Column(db.Unicode(100)) ## Possible common name of this group, i.e. Gamma_0(N)
    latex_name = db.Column(db.Unicode(100)) ## Possible common name of this group, i.e. Gamma_0(N)    
    ## We represent the permutations by strings (or?)
    p2 = db.Column(db.UnicodeText)
    p3 = db.Column(db.UnicodeText)
    pT = db.Column(db.UnicodeText)     # The permutation for T=RS
    generalised_level=Column(db.Integer)
    is_congruence = db.Column(db.Boolean)
    is_psl_rep = db.Column(db.Integer)
    is_pgl_rep = db.Column(db.Integer)
    # = 1 if G^* is conjugate to G
    is_symmetric = db.Column(db.Integer)
    # has modular correspondence
    # = 1 if G has a modular correspondence of
    has_modular_correspondence = db.Column(db.Integer)
    _modular_correspondences = db.relationship('Modular_correspondence_class',uselist=True,backref=db.backref('group'))
    modular_correspondences = association_proxy('_modular_correspondences','desc',creator = lambda (a,b,c,d,desc) : Modular_correspondence_class(a=a,b=b,c=c,d=d,desc=desc))
    
    symmetry_map = db.Column(db.UnicodeText)
    quotient_group = db.Column(db.UnicodeText)

    ## In case I come up eith something else to be included
    meta = db.Column(db.UnicodeText)
    extra_information = db.Column(db.UnicodeText)

    _cusps = db.relationship('Cusp_class',backref=db.backref('groups'))
    cusps = association_proxy('_cusps','name',
                              creator= lambda (a,b,w):Cusp_class(a=int(a),b=int(b),width=int(w)))
    ## Signature:
    signature_id = db.Column(db.Integer, db.ForeignKey('Signature_class.id'))
    _signature = db.relationship('Signature_class',backref=db.backref('groups'),uselist=True) #,backref=db.backref('group'))
    signature = association_proxy('_signature','name',
                                  creator = lambda (ix,nu,e2,e3,g):Signature(ix=int(ix),nu=int(nu),e2=int(e2),e3=int(e3),g=int(g)))


    # Subgroups of self
    subgroups = db.relationship(
                    'PSL2Zsubgroup',secondary=SubgroupRelationship,
                    primaryjoin=SubgroupRelationship.c.supergroup_id==id,
                    secondaryjoin=SubgroupRelationship.c.subgroup_id==id,
                    backref="supergroups")
   # Note attribute 'supergroups' is created automatically.


    def __repr__(self):
        if not isinstance(self.name,Column):
            if self.name <> None and self.name <> "":
                return self.name
        s = "Subgroup of PSL(2,Z) of index {0} given by permutations ".format(self.psl2z_index)
        s+= " {0} (order 2) and {1} (order 3)".format(self.p2,self.p3)
        return s

    def __latex__(self):
        if not isinstance(self.latex_name,Column):
            if self.latex_name <> None and self.latex_name <> "":
                return self.latex_name
        s = "Subgroup of $\mathrm{PSL}(2,\mathbb{Z})$ of index ${0}$ given by permutations ".format(self.psl2z_index)
        s+= " ${0}$ (order 2) and ${1}$ (order 3)".format(self.p2,self.p3)
        return s        
    
    def S2(self):
        return  PermutationGroupElement(str(self.p2.replace(' ',',')))
    def S3(self):
        return PermutationGroupElement(str(self.p3.replace(' ',',')))


    def supergroups(self):
        q=Subgroup_DB.query.filter_by(group=self)
        return map(lambda x:x.group, q.all())

    def signature_as_tuple(self):
        r"""
        REturn the signature of self as a tuple
        (mu, h, e2, e3, g)
        """
        return (self.psl2z_index, self.nu, self.e2, self.e3, self.genus)

    def signature_as_string(self):
        r"""
        Return the signature of self as a string mu_h_e2_e3_g
        """
        return '{0:0>2}_{1:0>2}_{2:0>2}_{3:0>2}_{4:0>2}'.format(self.psl2z_index, self.nu, self.e2, self.e3, self.genus)

def Cusp(a,b,gid):
    r"""
    Interface to Cusp_class
    """
    a = int(a); b = int(b); gid= int(gid)
    res = Cusp_class.query.filter_by(a=a,b=b,group_id=gid)
    if res.count()>0:
        return res.first()
    return Cusp_class(a=a,b=b,gid=gid)

class Cusp_class(db.Model):
    r"""
    A cusp (i.e. a rational number)
    """
    __tablename__ = 'Cusp_class'
    id = db.Column('id', db.Integer, primary_key=True)
    a = db.Column(db.Integer)
    b = db.Column(db.Integer)
    width = db.Column(db.Integer)
    name = db.Column(db.UnicodeText)
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    db.UniqueConstraint('a','b','group_id', name='uix_1')

    def __init__(self,a,b,width):
        self.a=int(a); self.b=int(b)
        self.width=int(width)
        if self.b==0:
            s = "Infinity"
        s= '{0}/{1}'.format(self.a,self.b)
        self.name = unicode(s)

    def __repr__(self):
        return self.name


def Signature(ix,nu,e2,e3,g):
    r"""
    Query and fetch or create / insert a Signature_class element.
    """
    results = Signature_class.query.filter_by(psl2z_index=int(ix),nu=int(nu),e2=int(e2),e3=int(e3),genus=int(g))
    if results.count()==0:
        signature = Signature_class(ix=ix,nu=nu,e2=e2,e3=e3,g=g)
    elif results.count()==1:
        signature = results.one()
    else:
        raise ValueError," Have multiple instances in databsse of signature:({0},{1},{2},{3},{4}) ".format(ix,nu,e2,e3,g)
    return signature

class Signature_class(db.Model):
    r"""
    Class representing signatures, i.e. tuples of the form (ix,nu,e2,e3,g)
    where ix = index, h = number of cusps, e2 = number of elliptic points of order 2,
    e3= number of elliptic points of order 2 and g is the genus
    """
    __tablename__ = 'Signature_class'
    id = db.Column('id', db.Integer, primary_key=True)
    psl2z_index = db.Column(db.Integer)  ## the name 'index' seems to cause trouble
    genus = db.Column(db.Integer)
    e2 = db.Column(db.Integer)
    e3 = db.Column(db.Integer)
    nu  = db.Column(db.Integer)
    name = db.Column(db.UnicodeText)
    def __init__(self,ix,nu,e2,e3,g):
        self.psl2z_index=ix; self.nu=nu; self.e2=e2; self.e3=e3; self.genus=g
        s = "({0},{1},{2},{3},{4})".format(self.psl2z_index,self.nu,self.e2,self.e3,self.genus)
        self.name = unicode(s)
    def __repr__(self):
        return self.name
    def __getitem__(self,i):
            return (self.psl2z_index,self.nu,self.e2,self.e3,self.genus)[i]
    def tuple(self):
        return (self.psl2z_index,self.nu,self.e2,self.e3,self.genus)

    def __len__(self):
        return 5


class ZZmatrix(db.Model): 
    r"""
    Class representing a 2x2 integer matrix.
    """
    __tablename__ = 'ZZmatrix'
    id = db.Column('id', db.Integer, primary_key=True)
    a = db.Column(db.Integer)
    b = db.Column(db.Integer)
    c = db.Column(db.Integer)
    d = db.Column(db.Integer)
    st = db.Column(db.UnicodeText)
    latex_st = db.Column(db.UnicodeText)    
    uix = db.UniqueConstraint('a','b','c','d')
    
    def __init__(self,a=1,b=0,c=0,d=1):
        r"""
        Init self.
        """
        self.a = int(a)
        self.b = int(b)
        self.c = int(c)
        self.d = int(d)
        self.st = '[[{0},{1}],[{2},{3}]]'.format(self.a,self.b,self.c,self.d)
        self.st = unicode(self.st)
        self.latex_st = unicode("\\left(\\begin{{array}}{{rr}} {0} & {1} \\\\ {2} & {3} \\end{{array}}\\right)".format(self.a,self.b,self.c,self.d))
     
    
    def get_col_spec(self):
        return "MyMatrixType" #(%s)" % self.precision

    def _str(self):
        r"""
        String representation of self.
        """
        if self.st=='':
            self.st = '[[{0},{1}],[{2},{3}]]'.format(self.a,self.b,self.c,self.d)
        return self.st

    def matrix(self):
        r"""
        A sage matrix representing self.
        
        """
        return matrix(ZZ,2,2,[self.a,self.b,self.c,self.d])

    def list(self):
        r"""
        A list of the entries of self.
        """
        return [self.a,self.b,self.c,self.d]
    def _latex_(self):
        r"""
        Latex representation of self.
        """
        return self.latex_st
    
    def __repr__(self):
        r"""
        Representation of self.
        """
        return self.st

class GL2Zmatrix(ZZmatrix): 
    r"""
    Class for 2x2 matrices with integer entries and determinant =1.
    """
    db.CheckConstraint(' a*d-b*c = 1 OR a*d-b*c = -1', name='derminant1orminus1')

class SL2Zmatrix(GL2Zmatrix): 
    r"""
    Class for 2x2 matrices with integer entries and determinant =1.
    """
    db.CheckConstraint('a*d-b*c = 1', name='derminant1')    

class Modular_correspondence_class(ZZmatrix):
    r"""
    A modular correspondence is given by a matrix A with AGA^-1 = G, A^2 in G and A preserve cusp classes.
    
    """
    __tablename__ = 'Modular_correspondence_class'
    modular_corr_id = db.Column('id', db.Integer, db.ForeignKey('ZZmatrix.id'),
                                                primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    desc = db.Column(db.UnicodeText)
    def __init__(self,a,b,c,d,desc):
        super(Modular_correspondence_class,self).__init__(a,b,c,d)
        #self.a=a
        #self.b=b
        #self.c=c
        #self.d=d
        self.desc=desc
    
class Coset_rep_class(SL2Zmatrix):
    r"""
    A coset representative is given by a
    
    """
    __tablename__ = 'Coset_rep_class'
    coset_rep_id = db.Column('id', db.Integer, db.ForeignKey('ZZmatrix.id'),
                                                primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    
class Generator_class(SL2Zmatrix):
    r"""
    A coset representative is given by a
    
    """
    __tablename__ = 'Generator_class'    
    generator_id = db.Column('id', db.Integer, db.ForeignKey('ZZmatrix.id'),
                                                primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))

    
