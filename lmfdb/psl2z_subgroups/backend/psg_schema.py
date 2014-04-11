#from elixir import Entity,Field,session,setup_all,create_all,ManyToOne,OneToMany,ManyToMany,using_options

import flask
from sage.all import PermutationGroupElement
from sqlalchemy.ext.associationproxy import association_proxy
#association_proxy = sqlalchemy.ext.associationproxy.association_proxy
#from sl2z_subgroups import db
from lmfdb.psl2z_subgroups import db

saInteger = db.Integer
Unicode   = db.Unicode
UnicodeText   = db.UnicodeText
Boolean = db.Boolean
Column = db.Column


class Subgroup_DB(db.Model):
    r"""
    Class representing subgroups of groups given as elements of PSL2Zsubgroup.
    """
    __tablename__ = 'Subgroup'
    id = db.Column('id', db.Integer, primary_key=True)
    supergroup_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    subg_index = Column(saInteger)
    # The group of self 
    group = db.relationship('PSL2Zsubgroup',primaryjoin = "Subgroup_DB.group_id == PSL2Zsubgroup.id") 

    def index(self):
        return self.subg_index
    def __repr__(self):
        return 'Subgroup of {0} of index {1}'.format(self.supergroup,self.subg_index)

class Conjugacy_class_psl(db.Model):
    r"""
    Class representing PSL(2,Z)-conjugacy classes of subgroups.
    """
    __tablename__ = 'Conjugacy_class_psl'
    id = db.Column(db.Integer, primary_key=True)
    representative_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
#    _psl_conjugates = db.relationship('Conjugacy_class_elt',foreign_keys=Conjugacy_class_elt.cc_id)
    _psl_conjugates = db.relationship('Conjugacy_class_elt',backref='conjugacy_class_psl',
                                      primaryjoin="Conjugacy_class_elt.conjugacy_class_psl_id==Conjugacy_class_psl.id")
    psl_conjugates = association_proxy('_psl_conjugates','group',
                                       creator = lambda (G,m): Conjugacy_class_elt(group=G,map_matrix=m))
    representative = db.relationship('PSL2Zsubgroup')
    def __repr__(self):
        return "List of {0} conjugates of {1}".format(len(self.psl_conjugates),self.representative)
    def length(self):
        return len(self.psl_conjugates)

class Conjugacy_class_pgl(db.Model):
    r"""
    Class representing PGL(2,Z)-conjugacy classes of subgroups.
    """
    __tablename__ = 'Conjugacy_class_pgl'
    id = db.Column(db.Integer, primary_key=True)
    _pgl_conjugates = db.relationship('Conjugacy_class_elt',backref='conjugacy_class_pgl',
                                     primaryjoin="Conjugacy_class_elt.conjugacy_class_pgl_id==Conjugacy_class_pgl.id") #,foreign_keys=db.ForeignKey('Conjugacy_class_elt.conjugacy_class_pgl_id'))
    pgl_conjugates = association_proxy('_pgl_conjugates','group',
                                       creator = lambda (G,m): Conjugacy_class_elt(group=G,map_matrix=m))
    representative_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    representative = db.relationship('PSL2Zsubgroup')
    def __repr__(self):
        return "List of {0} conjugates of {1}".format(len(self.pgl_conjugates),self.representative)
    def length(self):
        return len(self.pgl_conjugates)
  
    
class Conjugacy_class_elt(db.Model):
    r"""
    Element of a conjugacy class. Contains a group and a map taking it to the representative.
    """
    id =  db.Column('id', db.Integer, primary_key=True)
    conjugacy_class_psl_id= db.Column(db.Integer, db.ForeignKey('Conjugacy_class_psl.id'))
    conjugacy_class_pgl_id= db.Column(db.Integer, db.ForeignKey('Conjugacy_class_pgl.id'))        
    #conjugacy_class =  db.relationship('Conjugacy_class_psl',primaryjoin = "Conjugacy_class_elt.cc_id == Conjugacy_class_psl.id")
    #                                   #db.ForeignKey('conjugacy_classes_psl.id'))
    group_id= db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))    
    group = db.relationship('PSL2Zsubgroup',
                            primaryjoin = "Conjugacy_class_elt.group_id == PSL2Zsubgroup.id")
    map_matrix = db.Column(UnicodeText)    
    def __repr__(self):
        return '{0} conjugate by {1}'.format(self.group.__repr__(),self.map_matrix)

# class Generator_class(db.Model):
#     r"""
#     A generator represented as a 2x2 matrix [[a,b],[c,d]] with a,b,c,d integers and ad-bc = 1 
#     """
#     id = db.Column('id', db.Integer, primary_key=True)
#     matrix = db.relationship('SL2Zmatrix_class',uselist=False)    
#     gen_of_id = db.Column(db.Integer, db.ForeignKey('gen_of.id'))    
#     def sage_matrix(self):
#         return self.matrix.sage_matrix()
#     def sage_SL2Z(self):
#         return self.matrix.sage_SL2Z()
#     def short_string(self):
#         return self.matrix.short_string() #'[{0},{1},{2},{3}]'.format(self.a,self.b,self.c,self.d)    

# class Coset_rep_class(db.Model):
#     r"""
#     A coset representative represented as a 2x2 matrix [[a,b],[c,d]] with a,b,c,d integers and ad-bc = 1 
#     """
#     id = db.Column('id', db.Integer, primary_key=True)
#     matrix = db.relationship('SL2Zmatrix_class',uselist=False)
#     #a = db.Column(db.Integer)
#     #b = db.Column(db.Integer)
#     #c = db.Column(db.Integer)
#     #d = db.Column(db.Integer)
#     coset_rep_of_id = db.Column(db.Integer, db.ForeignKey('coset_rep_of.id'))    
#     def sage_matrix(self):
#         return self.matrix.sage_matrix()
#     def sage_SL2Z(self):
#         return self.matrix.sage_SL2Z()
#     def short_string(self):
#         return self.matrix.short_string() #'[{0},{1},{2},{3}]'.format(self.a,self.b,self.c,self.d)
import sqlalchemy.types as types

class SL2ZmatrixType(types.UserDefinedType):    
    impl = types.Unicode
    def __init__(self): #,a=1,b=0,c=0,d=1):
        pass
        #        self.a = a
        #        self.b = b
        #        self.c = c
        #        self.d = d
        #        self.value = '[{0},{1},{2},{3}]'.format(a,b,c,d) 
    def get_col_spec(self):
       return "MyMatrixType" #(%s)" % self.precision
    def process_bind_param(self, value, engine):
        return unicode(value) #jsonpickle.encode(value))

    def process_result_value(self, value, engine):
        if value:
            return value # jsonpickle.decode(value)
        else:
            # default can also be a list
            return ''
        
# class SL2Zmatrix_class(db.Model):
#     r"""
#     A 2x2 matrix [[a,b],[c,d]] with a,b,c,d integers and ad-bc = 1 
#     """
#     id = db.Column('id', db.Integer, primary_key=True)
#     a = db.Column(db.Integer)
#     b = db.Column(db.Integer)
#     c = db.Column(db.Integer)
#     d = db.Column(db.Integer)
#     coset_rep_of_id = db.Column(db.Integer, db.ForeignKey('coset_rep_of.id'))
#     gen_of_id = db.Column(db.Integer, db.ForeignKey('gen_of.id'))    
#     #if a*d-b*c <> 1:
#     #    raise ValueError,'[{0},{1},{2},{3}] not in SL(2,Z)!'.format(a,b,c,d)
    
#     def sage_matrix(self):
#         return sage.all.matrix(ZZ,2,2,[self.a,self.b,self.c,self.d])
#     def sage_SL2Z(self):
#         return sage.all.SL2Z([self.a,self.b,self.c,self.d])
#     def short_string(self):
#         return '[{0},{1},{2},{3}]'.format(self.a,self.b,self.c,self.d)
    
    
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
#    using_options(metadata=sl2zsubgroup_metadata, session=sl2zsubgroup_session,tablename="sl2z_subgroups")
    id = db.Column('id', db.Integer, primary_key=True)
    ## Use the signature as primary keys
    psl2z_index = Column(saInteger)  ## the name 'index' seems to cause trouble 
    genus = Column(saInteger)
    e2 = Column(saInteger)
    e3 = Column(saInteger)
    nu  = Column(saInteger)
    ## Relation to a list of coset representatives
   #  _coset_reps = db.relationship('Coset_rep_class',backref='coset_rep_of',
#                                   primaryjoin="SL2Zmatrix_class.coset_rep_of_id==PSL2Zsubgroup.id")
#     #,foreign_keys=db.ForeignKey('SL2Zmatrix_class.coset_rep_of_id'))
#     coset_reps = association_proxy('_coset_reps','short_string',
#                               creator= lambda (a,b,c,d): Coset_rep_class(matrix=SL2Zmatrix_class(a=a,b=b,c=c,d=d)))    
#     ## Relation to a list of generators
#     _gens = db.relationship('Generator_class',backref='gen_of',
#                             primaryjoin="SL2Zmatrix_class.gen_of_id==PSL2Zsubgroup.id")
# #,foreign_keys=db.ForeignKey('SL2Zmatrix_class.gen_of_id')) 
#     gens = association_proxy('_gens','short_string',
#                               creator= lambda (a,b,c,d): Generator_class(SL2Zmatrix_class(a=a,b=b,c=c,d=d)))
    coset_reps = Column(SL2ZmatrixType,default=u'')
    generators = Column(SL2ZmatrixType,default=u'')
    #gens = Column(UnicodeText,default=u"")
    
    label = Column(Unicode(100))  ## Automatically generated label for referencing (does this make sense to use?) 
    name = Column(Unicode(100)) ## Possible common name of this group, i.e. Gamma_0(N)
    ## We represent the permutations by strings (or?)
    p2 = Column(UnicodeText)
    p3 = Column(UnicodeText)
    generalised_level=Column(saInteger)
    is_congruence = Column(Boolean)
    is_psl_rep = Column(saInteger)
    is_pgl_rep = Column(saInteger)    
    is_symmetric = Column(saInteger)
    symmetry_map = Column(UnicodeText)
    quotient_group = Column(UnicodeText)
    
    #cusp_id = db.Column(db.Integer, db.ForeignKey('cusp.id'))
    _cusps = db.relationship('Cusp_class',backref=db.backref('group'))
    cusps = association_proxy('_cusps','name',
                              creator= lambda (a,b):Cusp_class(a=int(a),b=int(b)))
    
    ## Signature:
    _signature = db.relationship('Signature_class',backref=db.backref('group')) #,backref=db.backref('group'))
    signature = association_proxy('_signature','name',
                            creator = lambda (ix,nu,e2,e3,g):Signature_class(ix=int(ix),nu=int(nu),e2=int(e2),e3=int(e3),g=int(g)))

    #    supergroups = AssociationProxy('supergroups_as_supg','group',
#                             creator= lambda (G,index):Supergroup_DB(supg_index=int(index),group=G))
## Relationships
    #conjugates = ManyToMany('SL2Zsubgroup')
    #subgroups  = ManyToMany('SL2Zsubgroup')
    #supergroups  = ManyToMany('SL2Zsubgroup')

    # Subgroups of self    
    _subgroups = db.relationship('Subgroup_DB',backref=db.backref('supergroup'),
                                 foreign_keys=Subgroup_DB.supergroup_id)
    subgroups = association_proxy('_subgroups','group',
                                  creator= lambda (G,index):Subgroup_DB(subg_index=int(index),group=G))    

  
 

    def __repr__(self):
        if not isinstance(self.name,Column):
            if self.name <> None and self.name <> "":
                return self.name   
        s = "Subgroup of PSL(2,Z) of index {0} given by permutations ".format(self.psl2z_index)
        s+= " {0} (order 2) and {1} (order 3)".format(self.p2,self.p3)
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
    __tablename__ = 'Cusp'
    id = db.Column('id', db.Integer, primary_key=True)
    a = Column(saInteger)
    b = Column(saInteger)
    name = Column(UnicodeText)
    #group = db.relationship('SL2Zsubgroup', backref='cusps')
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
    #group = ManyToOne(SL2Zsubgroup)
    def __init__(self,a,b):
        self.a=a; self.b=b
        if self.b==0:
            s = "Infinity"
        s= '{0}/{1}'.format(self.a,self.b)
        self.name = unicode(s)
        
    def __repr__(self):
        return self.name
        #if self.b==0:
        #    return "Infinity"
        #return "{0}/{1}".format(self.a,self.b)



# class Supergroup_DB(db.Model):
#     r"""
#     Class representing supergroups.
#     """
#     __tablename__ = 'Supergroup'
#     id = db.Column('id', db.Integer, primary_key=True)
#     supg_index = Column(saInteger)
#     subgroups = db.relationship('SL2Zsubgroup')
#     group = db.relationship('SL2Zsubgroup')
#     def index(self):
#         return self.supg_index
#     def __repr__(self):
#         return 'Supergroup {0} of {1}'.format(self.group,self.supergroups)



# class Conjugate_group_PGL_DB(db.Model):
#     r"""
#     Class representing subgroups.
#     """
#     __tablename__ = 'Conjugate_group_PGL'
#     #using_options(metadata=sl2zsubgroup_metadata, session=sl2zsubgroup_session)    
#     id = db.Column('id', db.Integer, primary_key=True)
#     map_matrix = Column(UnicodeText)
#     map_perm = Column(UnicodeText)
#     pgl_conjugates = db.relationship('SL2Zsubgroup')
#     group = db.relationship('SL2Zsubgroup')
#     def __repr__(self):
#         return '{0} is PGL(2,Z) conjugate to {1}'.format(self.group,self.psl_conjugates)

def Signature(ix,nu,e2,e3,g):
    r"""
    Query and fetch or create / insert a Signature_class element.
    """
    results = Signature_class.query.filter_by(psl2z_index=int(ix),nu=int(nu),e2=int(e2),e3=int(e3),genus=int(g))
    if results.count()==0:
        signature = Signature_class(psl2z_index=ix,nu=nu,e2=e2,e3=e3,genus=g)
    elif results.count()==1:
        signature = Signature_class.one()
    else:
        raise ValueError," Have multiple instances in databsse of signature:({0},{1},{2},{3},{4}) ".format(ix,nu,e2,e3,g)
    return signature

class Signature_class(db.Model):
    r"""
    Class representing signatures, i.e. tuples of the form (ix,nu,e2,e3,g)
    where ix = index, h = number of cusps, e2 = number of elliptic points of order 2,
    e3= number of elliptic points of order 2 and g is the genus
    """
    __tablename__ = 'Signature'
    id = db.Column('id', db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('PSL2Zsubgroup.id'))
#    group = db.relationship('PSL2Zsubgroup',backref='signature',primaryjoin="PSL2Zsubgroup.id==Signature_class.group_id")
    psl2z_index = Column(saInteger)  ## the name 'index' seems to cause trouble 
    genus = Column(saInteger)
    e2 = Column(saInteger)
    e3 = Column(saInteger)
    nu  = Column(saInteger)
    name = Column(UnicodeText)
    def __init__(self,ix,nu,e2,e3,g):
        self.psl2z_index=ix; self.nu=nu; self.e2=e2; self.e3=e3; self.genus=g
        s = "({0},{1},{2},{3},{4})".format(self.psl2z_index,self.nu,self.e2,self.e3,self.genus)
        self.name = unicode(s)
    def __repr__(self):
        return self.name
