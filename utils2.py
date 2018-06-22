from math import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import graphviz as gv
import numbers
import random
import time
import matplotlib.pyplot as plt

########## LABELED SET ##########

class LabeledSet:  
    
    def __init__(self, input_dimension):
        '''
            initialize a labeled set with input dimension and ordinal attributes definition
        '''
        self.input_dimension = input_dimension
        self.nb_examples = 0
    
    def addExample(self,vector,label):
        '''
            vector : attribute values of example
            label : label of example
            add example to data set
        '''
        if (self.nb_examples == 0):
            self.x = np.array([vector])
            self.y = np.array([label])
            self.df = pd.DataFrame(np.array([vector + [label]]))
        else:
            self.x = np.vstack((self.x, vector))
            self.y = np.vstack((self.y, label))
            self.df.loc[len(self.df)] = np.array(vector + [label])
        
        self.nb_examples = self.nb_examples + 1
        
    def addExamples(self, vectors, label):
        '''
            vectors : array of examples
            label : label of examples
            add examples to data set
        '''
        if (self.nb_examples == 0):
            self.x = np.array(vectors)
            self.y = np.array([[label]] * vectors.shape[0])
            self.df = pd.DataFrame(np.hstack((vectors, np.array([[label]] * vectors.shape[0]))))
        else:
            self.x = np.vstack((self.x, vectors))
            self.y = np.vstack((self.y, np.array([[label]] * vectors.shape[0])))
            new_rows = pd.DataFrame(np.hstack((vectors, np.array([[label]] * vectors.shape[0]))))
            self.df = self.df.append(new_rows, ignore_index=True)
        
        self.nb_examples += vectors.shape[0]
    
    def getInputDimension(self):
        return self.input_dimension
    
    def size(self):
        return self.nb_examples
    
    def getX(self, i):
        return self.x[i]
        
    def getY(self, i):
        return(self.y[i])
    
    def get_df(self):
        return self.df

########## F-LAYERS ##########

class F_layer:
    '''
        object-wise local monotonicity measure 
    '''

    def value(self, w_i, att_values, label_values):
        '''
            return *-dsr(w_i) value
        '''
        raise NotImplementedError
        
    def get_name(self):
        '''
            return the name of the measure
        '''
        return self.name
        
    
    def equivalence_set(self, values, v):
        '''
            values : attribute values
            v : value to compute equivalence set 
            return equivalence set generated by the column containing values
        '''
        return values.index[values == v]
        
    def dominant_set(self, values, thr):
        '''
            values : attribute values
            thr : threshold to compute dominant set
            return dominant set generated by the column containing values
        '''
        return values.index[values >= thr]

    
class F_layer_rank(F_layer):
    '''
        object-wise local monotonicity measure 
    '''

    def value(self, w_i, att_values, label_values):
        raise NotImplementedError
        
class F_layer_non_rank(F_layer):
    '''
        object-wise local monotonicity measure 
    '''

    def value(self, w_i, att_values, label_values):
        raise NotImplementedError
        
class Ds(F_layer_non_rank):
    def value(self, w_i, att_values, label_values):
        '''
            w_i : index of threshold to compute dominant set
            att_values : attribute values
            label_values : label values
            return ds value of w_i generated by attribute containing att_values
        '''
        equivalence_set_att = np.array(self.equivalence_set(att_values, att_values[w_i]))
        equivalence_set_label = np.array(self.equivalence_set(label_values, label_values[w_i]))
        
        intersection = np.intersect1d(equivalence_set_att, equivalence_set_label)
        
        return (intersection.size * 1.0) / equivalence_set_att.size
    
class Dsr(F_layer_rank):
    
    def value(self, w_i, att_values, label_values):
        '''
            w_i : index of threshold to compute dominant set
            att_values : attribute values
            label_values : label values
            return dsr value of w_i generated by attribute containing att_values
        '''
        dominant_set_att = np.array(self.dominant_set(att_values, att_values[w_i]))
        dominant_set_label = np.array(self.dominant_set(label_values, label_values[w_i]))
        
        intersection = np.intersect1d(dominant_set_att, dominant_set_label)
        
        return (intersection.size * 1.0) / dominant_set_att.size
    
class Minds(F_layer_non_rank):
    def value(self, w_i, att_values, label_values):
        n = len(att_values)
        equivalence_set = np.array(self.equivalence_set(att_values, att_values[w_i]))
        min_l = np.iinfo(np.int32).max
        
        for w_h in equivalence_set:
            equivalence_att = np.array(self.equivalence_set(att_values, att_values[w_h]))
            equivalence_label = np.array(self.equivalence_set(label_values, label_values[w_h]))
            l = (np.intersect1d(equivalence_att, equivalence_label).size)
            if min_l > l:
                min_l = l
        return min_l * 1.0 / equivalence_set.size

    
class Mindsr(F_layer_rank):  
    def value(self, w_i, att_values, label_values):
        n = len(att_values)
        dominant_set = np.array(self.dominant_set(att_values, att_values[w_i]))
        equivalence_set = np.array(self.equivalence_set(att_values, att_values[w_i]))
        min_l = np.iinfo(np.int32).max
        
        for w_h in equivalence_set:
            dominant_att = np.array(self.dominant_set(att_values, att_values[w_h]))
            dominant_label = np.array(self.dominant_set(label_values, label_values[w_h]))
            l = (np.intersect1d(dominant_att, dominant_label).size)
            if min_l > l:
                min_l = l
        return min_l * 1.0 / dominant_set.size


class Maxds(F_layer_non_rank):
    
    def value(self, w_i, att_values, label_values):
        n = len(att_values)
        equivalence_set = np.array(self.equivalence_set(att_values, att_values[w_i]))
        max_l = np.iinfo(np.int32).min
        
        for w_h in equivalence_set:
            equivalence_att = np.array(self.equivalence_set(att_values, att_values[w_h]))
            equivalence_label = np.array(self.equivalence_set(label_values, label_values[w_h]))
            l = (np.intersect1d(equivalence_att, equivalence_label).size)
            if max_l < l:
                max_l = l  
                
        return max_l * 1.0 / equivalence_set.size
    
class Maxdsr(F_layer_rank):
    
    def value(self, w_i, att_values, label_values):
        n = len(att_values)
        dominant_set = np.array(self.dominant_set(att_values, att_values[w_i]))
        equivalence_set = np.array(self.equivalence_set(att_values, att_values[w_i]))
        max_l = np.iinfo(np.int32).min
        
        for w_h in equivalence_set:
            dominant_att = np.array(self.dominant_set(att_values, att_values[w_h]))
            dominant_label = np.array(self.dominant_set(label_values, label_values[w_h]))
            l = (np.intersect1d(dominant_att, dominant_label).size)
            if max_l < l:
                max_l = l 
                
        return max_l * 1.0 / dominant_set.size
    
class Avgds(F_layer_non_rank):
    
    def value(self, w_i, att_values, label_values):
        n = len(att_values)
        s = 0

        equivalence_set = np.array(self.equivalence_set(att_values, att_values[w_i]))

        for w_h in equivalence_set:
            equivalence_att = np.array(self.equivalence_set(att_values, att_values[w_h]))
            equivalence_label = np.array(self.equivalence_set(label_values, label_values[w_h]))
            s += (np.intersect1d(equivalence_att, equivalence_label).size)
            
        return ((1.0/equivalence_set.size)* s) / (1.0 * equivalence_set.size)
    
class Avgdsr(F_layer_rank):
    
    def value(self, w_i, att_values, label_values):
        n = len(att_values)
        s = 0
        
        dominant_set = np.array(self.dominant_set(att_values, att_values[w_i]))
        equivalence_set = np.array(self.equivalence_set(att_values, att_values[w_i]))

        for w_h in equivalence_set:
            dominant_att = np.array(self.dominant_set(att_values, att_values[w_h]))
            dominant_label = np.array(self.dominant_set(label_values, label_values[w_h]))
            s += (np.intersect1d(dominant_att, dominant_label).size)
            
        return ((1.0/equivalence_set.size)* s) / (1.0 * dominant_set.size)

    
########## G-LAYERS ##########

class G_layer:
    '''
        object-wise local non-monotonicity measure
    '''
        
    def value(self, f_value):
        raise NotImplementedError
        
class Log(G_layer):    
    def value(self, f_value):
        '''
            f_value : value computed by f_layer
            return -log_2(f_value)
        '''
        return -log(f_value, 2) 
    
class One_minus(G_layer):    
    def value(self, f_value):
        '''
            f_value : value computed by f_layer
            return 1 - f_value
        '''
        return 1 - f_value
    
class Frac(G_layer):
    def value(self, f_value):
        '''
            f_value : value computed by f_layer
            return -log(f_value) / f_value
        '''
        return -log(f_value, 2) / (1.0 * f_value)
    
########## H-LAYERS ##########

class H_layer:
    '''
        aggregated local non-monotonicity measure
    '''
        
    def value(self, g_values, n):
        raise NotImplementedError
        
class Sum(H_layer):    
    def value(self, g_values, n):
        '''
            return (1/n) * sum(g_values)
        '''
        return (1.0/n) * np.sum(g_values)
    
########## GENERIC DISCRIMINATION MEASURE ##########

class Gdm:
    '''
        Generic rank discrimination measure
    '''
    def __init__(self, h, g, f):
        '''
            h : object-wise local monotonicity measure 
            g : object-wise local non-monotonicity measure 
            f : aggregated local non-monotonicity measure
            labeled_set : labeled set
        '''
        self.h = h 
        self.g = g
        self.f = f
    
    def value(self, att_values, label_values):
        g_f = []
        n = len(att_values)
        
        for i in range(n):
            f_value = self.f.value(i, att_values, label_values)
            g_value = self.g.value(f_value)
            g_f.append(g_value)
        
        return self.h.value(g_f, n) 
    
########## DECISION TREE CONSTRUCTION ##########

def discretize(H, att_values, label_values):
    n = len(att_values)
    ind = np.argsort(att_values, axis=0)
    
    binary_att = pd.Series(np.array([1] * n))
    
    thresholds = []
    H_values = []
    
    for i in range(n-1):
        current = att_values[ind[i]]
        current_label = label_values[ind[i]]
        lookahead = att_values[ind[i+1]]
        lookahead_label = label_values[ind[i+1]]
        binary_att[ind[i]] = 0
        
        if current == lookahead or current_label == lookahead_label:
            continue
        else:
            thresholds.append((current + lookahead) / 2.0)
            h = H.value(binary_att, label_values)
            H_values.append(h)
    
    min_entropy = min(H_values)
    min_threshold = thresholds[np.argmin(H_values)]
    return (min_threshold, min_entropy)
            
def majority_class(labeled_set, labels):
    '''
        labeled_set : labeled set
        label : list of labels
        return majority class in labeled_set
    '''
    classes_size = []
    
    for label in labels:
        classes_size.append(len(labeled_set.x[np.where(labeled_set.y == label),:][0]))

    return labels[np.argmax(np.array(classes_size))]

def constant_lambda(labeled_set):
    '''
        labeled_set : labeled set
        return true if all objects in labeled_set share the same label, false otherwise
    '''
    labels = labeled_set.y
    return np.all(labels == labels[0,:], axis=0)[0]

def shannon(P):
    '''
        P : class distribution
        compute Shannon entropy
    '''
    Hs = 0
    k = len(P)
    for p_i in P:
        tmp = 0
        if p_i != 0:
            tmp = p_i * log(p_i, k)
        Hs += tmp
    
    return -Hs

def entropy(labeledSet, labels, name):
    P = []

    # get class distribution
    for label in labels:
        P.append(len(labeledSet.x[np.where(labeledSet.y == label),0:labeledSet.getInputDimension()][0]) / (1.0 * labeledSet.size()))
    
    # shannon entropy
    return shannon(P)

def divide(Lset, att, threshold):
    '''
        Lset : labeled_set
        att : index of attribute to divide
        threshold : threshold value
        divide Lset into two sub-sets : one with values for att <= threshold, one with values > threshold
    '''
    E1 = LabeledSet(Lset.getInputDimension())
    E2 = LabeledSet(Lset.getInputDimension())
    
    # Separate data according to threshold
    for i in range(Lset.size()):
        if Lset.getX(i)[att] <= threshold:
            E1.addExample(Lset.getX(i), Lset.getY(i))
        else:
            E2.addExample(Lset.getX(i), Lset.getY(i))
    
    return E1, E2

class BinaryTree:
    '''
        Binary tree
        deal with numeric attributes (ordinal attributes have to be pre-treated and must be orderable)
        deal with multi-class classification (classes must be orderable)
    '''
    def __init__(self):
        self.attribute = None
        
        # leaf
        self.label = None
        self.labeled_set = None
        
        # internal node
        self.threshold = None
        self.inf = None
        self.sup = None
        
    def isLeaf(self):
        """ 
            return True if tree is a leaf
        """
        return self.attribute == None
    
    def add_children(self, inf, sup, att, threshold):
        """
            inf, sup : trees
            att : index of attribute
            threshold : threshold value
            add children to node
        """
        self.attribute = att
        self.threshold = threshold
        self.inf = inf
        self.sup = sup
    
    def addLeaf(self,label, labeled_set):
        """ 
            add leaf corresponding to label
        """
        self.label = label
        self.labeled_set = labeled_set
        
    def classify(self,example):
        """ 
            example : numpy array in labeled set
            classify example
        """
        if self.isLeaf():
            return self.label
        else:
            if example[self.attribute] <= self.threshold:
                return self.inf.classify(example)
            return self.sup.classify(example)
                
    def to_graph(self, g, prefix='A'):
        """ 
            build a representation of the tree
        """
        if self.isLeaf():
            g.node(prefix,str(self.label),shape='box')
        else:
            g.node(prefix, str(self.attribute))
            
            g.node(prefix, str(self.attribute))
            self.inf.to_graph(g,prefix+"l")
            self.sup.to_graph(g,prefix+"r")
            g.edge(prefix,prefix+"l", '<='+ str(self.threshold))
            g.edge(prefix,prefix+"r", '>'+ str(self.threshold))
        return g
    
    def get_depth(self):
        '''
            return tree depth
        '''
        if self.isLeaf():
            return 1
        else:
            return 1 + max(self.inf.get_depth(), self.sup.get_depth())
        
    def get_nb_leaves(self):
        '''
            return number of leaves
        '''
        if self.isLeaf():
            return 1
        else:
            return self.inf.get_nb_leaves() + self.sup.get_nb_leaves()
        
    def is_rule_monotone(self):
        '''
            return true if tree is rule monotone, false otherwise
        '''
        if (self.inf.isLeaf()) and (self.sup.isLeaf()):
            if self.inf.label > self.sup.label:
                return False
            return True
        elif self.inf.isLeaf():
            return self.sup.is_rule_monotone()
        elif self.sup.isLeaf():
            return self.inf.is_rule_monotone()
        else:
            return self.inf.is_rule_monotone() and self.sup.is_rule_monotone()
        
    def get_ratio_non_monotone_pairs(self):
        '''
            return average ratio between number of pairwise non-monotone label comparisons and number of pairs
        '''
        if (self.inf.isLeaf()) and (self.sup.isLeaf()):
            
            inf_set = self.inf.labeled_set
            sup_set = self.sup.labeled_set
            
            n_inf = inf_set.size()
            n_sup = sup_set.size()
            
            c = 0
            for i in range(n_inf):
                for j in range(n_sup):
                    if inf_set.getY(i) >= sup_set.getY(j):
                        c += 1
            return [((n_inf + n_sup) * (c * 1.0) / (n_inf * n_sup), n_inf +n_sup)]
            
            
        elif self.inf.isLeaf():
            return self.sup.get_ratio_non_monotone_pairs()
            
        elif self.sup.isLeaf():
            return self.inf.get_ratio_non_monotone_pairs()
            
        else:
            t_inf = self.inf.get_ratio_non_monotone_pairs()
            t_sup = self.sup.get_ratio_non_monotone_pairs()
            
            
            t_inf.extend(t_sup)
            return t_inf
        
def build_DT(labeled_set, H, H_stop, measureThreshold, maxDepth, percMinSize, labels, current_depth):
    '''
        labeled_set : labeled set
        H : rank discrimination measure used for discretization
        H_stop : discrimination measure (shannon, gini ...) used for stopping condition
        measure_threshold : lower bound for H_stop
        max_depth : maximum length of a path from the root to a leaf node
        percMinSize : sets the minimum size of the current object set labeled_set
        build decision tree recursively
    '''
    
    h = entropy(labeled_set, labels, "shannon")
        
    if (h <= measureThreshold) or (labeled_set.size() <= percMinSize * labeled_set.size()) or (constant_lambda(labeled_set)) or (current_depth > maxDepth):        
        leaf = BinaryTree()
        leaf.addLeaf(majority_class(labeled_set, labels), labeled_set)
        return leaf
    
    m = labeled_set.getInputDimension()
    min_threshold = None
    min_attribute = None
    
    h_values = []
    thresholds = []
    
    for a_j in range(m):
        
        # all objects share the same value for attribute a_j
        if np.all(labeled_set.x == labeled_set.x[0,:], axis = 0)[a_j]:
            thresholds.append(None)
            h_values.append(np.iinfo(np.int32).max)
            continue
        
        threshold, h = discretize(H, labeled_set, a_j)
        thresholds.append(threshold)
        h_values.append(h)
        
    min_threshold = thresholds[np.argmin(h_values)]
    min_attribute = np.argmin(h_values)
    
    
    inf_set, sup_set = divide(labeled_set, min_attribute, min_threshold)
    bt = BinaryTree()
    
    if inf_set.size() == 0:
        bt.addLeaf(majority_class(sup_set, labels), sup_set)
        return bt
    if sup_set.size() == 0:
        bt.addLeaf(majority_class(inf_set, labels), inf_set) 
        return bt
    
    inf_bt = build_DT(inf_set, H, H_stop, measureThreshold, maxDepth, percMinSize, labels, current_depth+1)
    sup_bt = build_DT(sup_set, H, H_stop, measureThreshold, maxDepth, percMinSize, labels, current_depth+1)
    bt.add_children(inf_bt, sup_bt, min_attribute, min_threshold)
    return bt

########## CLASSIFIERS ##########

class Classifier:
    def __init__(self,input_dimension):
        raise NotImplementedError("Please Implement this method")
    
    def predict(self,x):
        '''
            x : example
            compute prediction on x => return score
        '''
        raise NotImplementedError("Please Implement this method")

    def train(self,labeled_set):
        '''
            labeled_set : labeled set
            train model on labeled_set
        '''
        raise NotImplementedError("Please Implement this method")
    
    def accuracy(self,labeled_set):
        '''
            labeled_set : labeled_set
            return accuracy score on whole dataset
        '''
        nb_ok=0
        for i in range(labeled_set.size()):
            score = self.predict(labeled_set.getX(i))
            if (score == labeled_set.getY(i)):
                nb_ok = nb_ok+1
        acc = nb_ok/(labeled_set.size() * 1.0)
        return acc    
    
class RDMT(Classifier):
    '''
        Rank discrimination measure tree 
    '''
    def __init__(self, H, H_stop, measureThreshold, maxDepth, percMinSize, labels):
        '''
            H : discrimination measure to minimize for splitting
            H_stop : discrimination measure (shannon, gini ...) used for stopping condition
            measureThreshold : lower bound for the discrimination measure H
            maxDepth : maximum length of a path from the root to a leaf node
            percMinSize : minimum size of the current object set 
            labels : list of classes
        '''
        self.H = H
        self.H_stop = H_stop
        self.measureThreshold = measureThreshold
        self.maxDepth = maxDepth
        self.percMinSize = percMinSize
        self.labels = labels
        self.root = None
        
    def predict(self,x):
        '''
            classify x using RDMT
            return prediction
        '''
        label = self.root.classify(x)
        return label
    
    def train(self,labeled_set):
        '''
            set : training set
            builds RDMT using set
        '''
        self.labeled_set = labeled_set
        self.root = build_DT(labeled_set,self.H, self.H_stop, self.measureThreshold, self.maxDepth, self.percMinSize, self.labels, 0)
    
    def plot(self):
        '''
            display tree
        '''
        gtree = gv.Digraph(format='png')
        return self.root.to_graph(gtree)   
    
    def get_depth(self):
        return self.root.get_depth()
    
    def get_nb_leaves(self):
        return self.root.get_nb_leaves()
    
    def is_rule_monotone(self):
        return self.root.is_rule_monotone()
    
    def get_ratio_non_monotone_pairs(self):
        t = np.array(self.root.get_ratio_non_monotone_pairs())
        r = t[:,0].sum() / t[:, 1].sum()
        return (t[:,0].sum() / t[:, 1].sum()) / t.shape[0]
        #n = self.labeled_set.size()
        #return ((n - t[:,1].sum()) + r * (t[:,1].sum())) / n
    
    def get_total_pairs(self):
        t = np.array(self.root.get_ratio_non_monotone_pairs())
        return t.shape[0]
    
    def MAE(self, labeled_set):
        '''
            labeled_set : labeled set for evaluating the performance of the algorithm
            return mean absolute error
        '''
        s = 0
        n = labeled_set.size()
        for i in range(n):
            x = labeled_set.getX(i)
            y = labeled_set.getY(i)
            s += fabs(self.predict(x) - y)
        return (1.0/n) * s

########## DATA SET GENERATION ##########

def generate_2Ddataset(a_j, k, n, noise, amplitude, ranges):
    '''
        a_j : monotone attribute
        k : number of labels
        n : number of examples to create 
        noise :  % of non-monotone noise
        amplitude : amplitude of noise
        ranges : array of arrays indicating, for each attribute, its min and max values
        return 2D dataset containing k classes and n examples, with a_j being the monotone attribute
    '''
    labeled_set = LabeledSet(2)
    p = round(n/k)
    r = n # remaining examples to add 
    
    current_min = ranges[a_j][0]
    total_range = ranges[a_j][1] - ranges[a_j][0]
    
    thresholds = []
    
    for q in range(k):
        current_max = current_min + (total_range / k) 

        if (current_max > ranges[a_j][1]):
            current_max = ranges[a_j][1]
        
        if (current_max < ranges[a_j][1] and q == k-1):
            current_max = ranges[a_j][1] 
        
        
        if (p < r) and (q==k-1):
            p = r

        
        monotone_values = np.random.uniform(current_min, current_max, size=(p,1))
        
        if noise > 0:
            sample_size = np.random.binomial(len(monotone_values), noise)
            sample = np.random.randint(0, len(monotone_values), size=sample_size)
            
            for e in sample:
                if random.random() < 0.5:
                    val = current_min - random.uniform(0, total_range * amplitude)
                    if (val < ranges[a_j][0]):
                        val = ranges[a_j][0]
                    monotone_values[e] = val
                else:
                    val = current_max + random.uniform(0, total_range * amplitude)
                    if (val > ranges[a_j][1]):
                        val = ranges[a_j][1]
                    monotone_values[e] = val
        
        thresholds.append((current_min,current_max) )
        
        if (a_j == 0):
            random_values = np.random.uniform(ranges[1][0], ranges[1][1], size=(p, 1))
            values = np.hstack((monotone_values, random_values))
        else:
            random_values = np.random.uniform(ranges[0][0], ranges[0][1], size=(p,1))
            values = np.hstack((random_values, monotone_values))
        
        for i in range(p):
            labeled_set.addExample(values[i].tolist(), q+1)
            
        current_min = current_max
        r -= p 
    return labeled_set, thresholds

def normalize(x, min_v, max_v):
    return ((x - min_v)*1.0) / (max_v - min_v) 

def generate_monotone_consistent_dataset(n, k):
    '''
        n : number of examples to create
        k : class number
        generate 2D monotone consistent dataset with n examples and k classes
            with function f(x1, x2) = 1 + x1 + (1/2) (x2^2 - x1^2)
    '''
    values = []
    x = []
    for i in range(n):
        x1 = random.uniform(0, 1)
        x2 = random.uniform(0, 1)
        x.append((x1, x2))
        v = 1 + x1 + (1/2) * (x2 * x2 - x1 * x1)
        values.append(v)
        
    max_v = max(values)
    min_v = min(values)
    results = []
    
    for i in range(n):
        results.append(normalize(values[i], min_v, max_v))
    
    x = [x for _, x in sorted(zip(results, x))]
    results = sorted(results)
    
    data = np.hstack((np.array(x), np.reshape(np.array([results]), (-1, 1))))
    
    monotone_set = LabeledSet(2)
    
    for i in range(k):
        if i == 0:
            examples = data[(data[:,2] <= 1.0/k)][:,:2]
            p = examples.shape[0]
        else:
            examples = data[(data[:,2] > (i*1.0)/k) & (data[:,2] <= (i+1.0)/k)][:,:2]
            p = examples.shape[0]
        monotone_set.addExamples(examples, np.array([[i+1]] * p))

    return monotone_set

def NMP(i, h, labeled_set):
    '''
        labeled_set : labeled set
        i, h : pair of indices in labeled_set
        return 1 if 
            (a1(w_i),...,am(w_i)) <= (a1(w_h),...,am(w_h)) and lambda(w_i) > lambda(w_h)
            or 
            (a1(w_i),...,am(w_i)) >= (a1(w_h),...,am(w_h)) and lambda(w_i) < lambda(w_h)
        0 otherwise
    '''
    w_i = labeled_set.getX(i)
    w_h = labeled_set.getX(h)
    if (np.sum(w_i - w_h)) <= 0 and (labeled_set.getY(i) > labeled_set.getY(h)):
        return 1
    if (np.sum(w_i - w_h)) >= 0 and (labeled_set.getY(i) < labeled_set.getY(h)):
        return 1
    return 0

def NMI1(labeled_set):
    '''
        labeled_set : labeled set
        return index of non-monotonicity NMI1
    '''
    n = labeled_set.size()
    
    s = 0
    for i in range(n):
        for j in range(i+1, n):
            s += NMP(i, h, labeled_set)
            
    return s / (n*n - n)

def NClash(x, y, labeled_set):
    '''
        labeled_set : labeled set
        x : example
        y : label of example
        return the number of examples that clash with x
    '''
    n = labeled_set.size()
    
    s = 0
    for i in range(n):
        z = labeled_set.getX(i)
        if (np.less_equal(z, x).all()) and (labeled_set.getY(i) > y):
            s += 1
        if (np.greater_equal(z, x).all()) and (labeled_set.getY(i) < y):
            s += 1
    return s
    
def generate_noisy_monotone_dataset(n, desired_NMI, lower_NMI, m, k, f):
    '''
        n : number of examples
        desired_NMI : desired non-monotonicity index
        lower_NMI : lower bound of NMI
        m : number of attributes
        k : number of ordinal class values
        f : non-decreasing monotone function
        return a dataset with the above specifications
    '''
    class_num_values = []
    x = []
    
    # step A :
    #   for each example, assign random values to the attributes
    #   compute the output as f(attribute values)
    for i in range(n):
        vector = np.random.uniform(0,1,m)
        x.append(vector)
        c = f(vector)
        class_num_values.append(c)
    
    # step B :
    #   normalize output values and sort all the examples in increasing order of normalized output values
    max_v = max(class_num_values)
    min_v = min(class_num_values)
    outputs = []
    
    for i in range(n):
        outputs.append(normalize(class_num_values[i], min_v, max_v))
    
    x = [x for _, x in sorted(zip(outputs, x))]
    outputs = np.reshape(np.array([sorted(outputs)]), (-1, 1))
    
    # step C : 
    #   assign ordinal values to the class such that the class values will be balanced
    data = np.hstack((np.array(x), np.reshape(np.array([outputs]), (-1, 1))))
    
    dataset = LabeledSet(m)
    
    for i in range(k):
        if i == 0:
            examples = data[(data[:,m] <= 1.0/k)][:,:m]
            p = examples.shape[0]
        else:
            examples = data[(data[:,m] > (i*1.0)/k) & (data[:,m] <= (i+1.0)/k)][:,:m]
            p = examples.shape[0]
        dataset.addExamples(examples, np.array([[i+1]] * p))
        
    current_NMI = NMI1(dataset)
    
    # step D
    while current_NMI < lower_NMI:
        r = random.sample(range(0, n), 2)
        x = dataset.getX(r[0])
        y = dataset.getY(r[0])
        
        if y == 1:
            # randomly select attribute values for xp that are <= relative to those of x
            xp = np.random.uniform(0, x, m)
            # class value that is > to y
            xp_y = random.randint(2, k+1)
        elif y == k+1:
            # randomly select attribute values for xp that are >= relative to those of x
            xp = np.random.uniform(x, 1, m)
            # class value that is < to y
            xp_y = random.randint(1, k)
        else:
            if random.uniform(0, 1) <= 0.5:
                xp = np.random.uniform(0, x, m)
                xp_y = random.randint(y+1, k+1)
            else:
                xp = np.random.uniform(x, 1, m)
                xp_y = random.randint(1, y-1)
        
        xs = dataset.getX(r[1])
        xs_y = dataset.getY(r[1])
        nclash_xs = NClash(xs, xs_y, dataset)
        nclash_xp = NClash(xp, xp_y, dataset)
        
        updated_NMI = nclash_xp - nclash_xs
        
        if updated_NMI < desired_NMI:
            dataset.x[r[1]] = xp
            dataset.y[r[1]] = xp_y
            current_NMI = updated_NMI
            
    return dataset
    
########## DISPLAY ##########    
    
def plot2DSet(labeled_set, title):
    labels = list(set([item for sublist in labeled_set.y.tolist() for item in sublist]))
    mark_dict = {
        ".":"point",
        ",":"pixel",
        "o":"circle",
        "v":"triangle_down",
        "^":"triangle_up",
        "<":"triangle_left",
        ">":"triangle_right",
        "1":"tri_down",
        "2":"tri_up",
        "3":"tri_left",
        "4":"tri_right",
        "8":"octagon",
        "s":"square",
        "p":"pentagon",
        "*":"star",
        "h":"hexagon1",
        "H":"hexagon2",
        "+":"plus",
        "D":"diamond",
        "d":"thin_diamond",
        "|":"vline",
        "_":"hline"
    }    
    S = []
    for label in labels:
        S.append(labeled_set.x[np.where(labeled_set.y == label),:][0])
    for i in range(len(labels)):
        plt.scatter(S[i][:,0],S[i][:,1],marker=list(mark_dict)[i])
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title(title)
    
def display_discretization(labeled_set, threshold, a_j, title):
    '''
        labeled_set : labeled_set
        threshold : value of threshold 
        a_j : index of discretized attribute
        title : plot title
        
        display 2D database along with threshold generated by discretization on attribute a_j
    '''
    plot2DSet(labeled_set, title)
    
    if (a_j == 0):
        max_v = ceil(max(labeled_set.x[:,1]))
        min_v = floor(min(labeled_set.x[:,1]))
        plt.plot([threshold, threshold], [min_v, max_v])
    else:
        max_v = ceil(max(labeled_set.x[:,0]))
        min_v = floor(min(labeled_set.x[:,0]))
        plt.plot([min_v, max_v], [threshold, threshold])

    plt.show() 
    
def display_discretizations_comparison(labeled_set, threshold1, threshold2, real_thresholds, a_j, title, l1, l2):
    '''
        labeled_set : labeled_set
        threshold1 : threshold generated by discretization on a_j with first measure
        threshold2 : threshold generated by discretization on a_j with second measure
        real_thresholds : list of real thresholds
        title : plot title
        l1 : label of threshold1 (discrimination measure name)
        l2 : label of threshold2 (discrimination measure name)
        plot thresholds generated by two different discrimination measures on attribute a_j of labeled_set
    '''
    plot2DSet(labeled_set, title)
    
    if (a_j == 0):
        max_v = ceil(max(labeled_set.x[:,1]))
        min_v = floor(min(labeled_set.x[:,1]))
        plt.plot([threshold1, threshold1], [min_v, max_v], color='green', label=l1)
        plt.plot([threshold2, threshold2], [min_v, max_v], color='red', label=l2)
        for i in range(len(real_thresholds)):
            threshold = real_thresholds[i]
            if i == 0:
                plt.plot([threshold, threshold], [min_v, max_v], color='black', label="real threshold")
            else:
                plt.plot([threshold, threshold], [min_v, max_v], color='black')
    else:
        max_v = ceil(max(labeled_set.x[:,0]))
        min_v = floor(min(labeled_set.x[:,0]))
        plt.plot([min_v, max_v], [threshold1, threshold1], color='green', label=l1)
        plt.plot([min_v, max_v], [threshold2, threshold2], color='red', label=l2)
        for i in range(len(real_thresholds)):
            threshold = real_thresholds[i]
            if i == 0:
                plt.plot([min_v, max_v], [threshold, threshold], color='black', label="real threshold")
            else:
                plt.plot([min_v, max_v], [threshold, threshold], color='black')
    plt.legend()
    plt.show() 

########## DATA SET SPLITTING ########## 

def split_dataset(labeled_set, percentage):
    '''
        labeled_set : labeled set to split
        percentage : percentage of examples to put in the training set
        return labeled_set split into two subsets
    '''
    n = labeled_set.size()
    
    train_set = LabeledSet(labeled_set.getInputDimension())
    test_set = LabeledSet(labeled_set.getInputDimension())
    
    labels = np.unique(labeled_set.y)
    
    for k in labels:
        examples = labeled_set.x[np.where(labeled_set.y == k),:][0]
        np.random.shuffle(examples)
        p = int(examples.shape[0] * (percentage/100.0))
        train_set.addExamples(examples[:p,:], np.array([[k]] * p))
        test_set.addExamples(examples[p:,:], np.array([[k]] * (examples.shape[0] - p)))
        
    return train_set,test_set

def get_ten_folds(labeled_set):
    sets = []
    labels = np.unique(labeled_set.y)
    k = labels.shape[0]
    n = labeled_set.size()
    starting_points = [0] * k
    ending_points = [-1] * k
        
    r = [0] * labels.shape[0] # remaining examples to add in each class
    
    for q in range(k):
        examples = labeled_set.x[np.where(labeled_set.y == labels[q]),:][0]
        r[q] = examples.shape[0]
    
    for i in range(10):
        dataset = LabeledSet(labeled_set.getInputDimension())
        
        for q in range(k):
            examples = labeled_set.x[np.where(labeled_set.y == labels[q]),:][0]
            p = int(round(examples.shape[0] / 10.0))
            if (i == 9) and (r[q] != p):
                ending_points[q] = examples.shape[0]
                r[q] = 0 
            else:
                ending_points[q] = starting_points[q] + p
                r[q] -= p
            
            dataset.addExamples(examples[starting_points[q]:ending_points[q],:], np.array([[labels[q]]] * (ending_points[q] - starting_points[q])))
            
            starting_points[q] = ending_points[q] 
        sets.append(dataset)
    return sets
    
    return (train_set, test_set)