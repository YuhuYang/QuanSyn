#!/usr/bin/env python
# coding: utf-8

import numpy as np
from scipy import optimize as op
import math
from sklearn.metrics import r2_score

def piotrovski_altmann_law(variant=None):
    """
    Piotrovski_Altmann Law, also called Language Evolution Law.

    Args:
        t(float): time scale.
        
    Parameters:
        a(float): denotes the moment in time when the progression of change stops accelerating and begins to decelerate (the point of inflection), 
        b(float): the overall speed of the change (the slope)
        C(float): its intensity (the height). 

    Returns:
        The portion or number of the new forms.
    """
    if variant == None:
        def func(t,a,b):
            return 1 / (1 + a * np.exp((-b) * t))
    if variant == "partial":
        def func(t,a,b,C):
            return C / (1 + a * np.exp((-b) * t))
    if variant == "reversiable":
        def func(t,a,b,C,c):
            return C / (1 + a * np.exp((-b) * t + c * t **2))
    return func  
    
def zipf_law(variant=None):
    """
    Zipf's Law.

    Args:
        r(int): frequency-rank of words.
    
    Parameters:
        C(float): constant.    
        b(float): the slope.

    Returns:
        The portion or number of the new forms.
    """
    if variant == None:
        def func(r, b,C ):
            return C * r ** -b
    return func

def menzerath_altmann_law(variant = None):
    """
    Menzerath-Altmann's Law.

    Args:
        x(int): consititution length.
    
    Parameters:
        a(float):     
        b(float): 
        c(float):

    Returns:
        The length of the whole construction.
    """
    if variant == "simplified form":
        def func(x, a, c):
            return a * math.e ** (-c*x)
    if variant == "complex form":
        def func(x, a, b, c):
            return a * x ** (-b) * math.e ** (-c*x)
    else:
        def func(x, a, b):
            return a * x ** -b
    return func

def heap_law(variant=None):
    """
   Heap's Law, also called Herdan's Law.

    Args:
        n(int): consititution length.
    
    Parameters:
        K(float):     
        beta(float): 

    Returns:
        The number of distinct words in an instanse text of size n construction.
    """
    if variant == None:
        def func(n, K, beta):
            return K * n ** beta
    return func

def brevity_law(variant=None):
    """
   Brevity Law, also called  Zipf's law of abbreviation.

    Args:
        F(int): word frequency.
    
    Parameters:
        a(float):     
        b(float): 

    Returns:
        word length.
    """
    if variant == None:
        def func(F, a, b):
            return a * F ** (-b)
    return func

laws = {
    'piotrovski_altmann': piotrovski_altmann_law,
    'zipf': zipf_law,
    'menzerath_altmann':menzerath_altmann_law,
    'menzerath':menzerath_altmann_law,
    'heap': heap_law,
    'herdan': heap_law,
    "brevity":brevity_law
}
    
def calculate_r_squared(y_actual, y_fit):
    # Calculate R-squared (coefficient of determination)
    mean_y_actual = np.mean(y_actual)
    ss_tot = np.sum((y_actual - mean_y_actual) ** 2)
    ss_res = np.sum((y_actual - y_fit) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared
    
def fit(data, law_name:str=None, variant=None, customized_law=None):
    """
    This is the core of this module. It can be used to fit laws conveniently.

    Args:
        data(np.array): it should consist of two lists or arrays, such as [[0,1,2,],[5,8,3]],
            the first element is x_data,and the second is y_data.
        law_name(str): the law you want to fit, such as "Zipf_law".
        variant(str): maybe some laws have variants.
        customized_law(function): the laws defined by you.

    Returns:
        parameters and r_aqured.
    """
    if law_name is not None and law_name not in laws:
        raise ValueError(f"Unsupported laws: {law_name}")
    elif law_name is None and customized_law is not None:
        fit_func = customized_law
    elif law_name in laws and customized_law is None:
        fit_func = laws[law_name](variant=variant)

    data = np.array(data)
    
    params, _ = op.curve_fit(fit_func, data[0], data[1])
    y_fit = fit_func(data[0], *params)
    r2 = r2_score(y_fit, data[1])
    return {'params':params, 'r^2':r2}
