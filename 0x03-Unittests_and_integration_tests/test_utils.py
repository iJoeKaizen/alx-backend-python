#!/usr/bin/env python3
"""
Utility functions module
"""
import requests
from functools import wraps

def access_nested_map(nested_map, path):
    """
    Access nested dictionary with given path
    """
    for key in path:
        if not isinstance(nested_map, dict) or key not in nested_map:
            raise KeyError(key)
        nested_map = nested_map[key]
    return nested_map

def get_json(url):
    """
    Fetch JSON from URL
    """
    response = requests.get(url)
    return response.json()

def memoize(func):
    """
    Memoization decorator to cache method results
    """
    cache = {}
    
    @wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper
