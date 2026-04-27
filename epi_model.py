import pandas as pd
import os

class EpidemicModel:
    def __init__(self):
        self.json_file = 'cities_data.json'
        self.base_loss = 10_000_000

    def load_data(self):
        if os.path.exists(self.json_file):
            try: return pd.read_json(self.json_file)
            except: pass
        return pd.DataFrame({
            'name': ['بغداد', 'البصرة', 'الموصل'], 
            'latitude': [33.3, 30.5, 36.3], 
            'longitude': [44.3, 47.7, 43.1], 
            'population': [8120000, 2900000, 1700000]
        })

    def calculate(self, df, beta, gamma, impact_value):
        beta_eff = beta * (1 - impact_value)
        df['infected_total'] = df['population'].apply(
            lambda p: int(p * (1 - (gamma/beta_eff))) if beta_eff > gamma else 0
        )
        df['risk_score'] = (df['infected_total'] / df['population']) * 100
        
        loss = self.base_loss + (90_000_000 * impact_value) if impact_value > 0 else 0
        saved = int(df['infected_total'].sum() * 0.08 * impact_value)
        return df, loss, saved