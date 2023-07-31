
import pandas as pd
from .models import Data
class MyClass:
    data = []
    
    def __init__(self):
        dataset = Data.objects.all()
        df = pd.DataFrame(list(dataset.values('data')))
        print(df)
        

