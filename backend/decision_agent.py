from datetime import datetime

class DecisionAgent:
    def __init__(self):
        self.risk_levels = {
            'low': (0, 0.3),
            'medium': (0.3, 0.7),
            'high': (0.7, 1.0)
        }
        
        self.response_policies = {
            'low': ['log', 'alert'],
            'medium': ['log', 'alert', 'rate_limit'],
            'high': ['log', 'alert', 'block_ip', 'isolate_host']
        }
    
    def assess_threat(self, prediction, confidence, learned_action=None):
        """Assess threat and determine response"""
        
        if prediction == 0:
            return {
                'threat_detected': False,
                'risk_level': 'none',
                'actions': [],
                'confidence': confidence,
                'learned_action_applied': False
            }
        
        risk_score = confidence
        risk_level = self._calculate_risk_level(risk_score)
        actions = self.response_policies.get(risk_level, ['log']).copy()
        
        # INTEGRATE LEARNING: Override with learned action
        learned_action_applied = False
        if learned_action:
            if learned_action == 'block_ip' and 'block_ip' not in actions:
                actions.append('block_ip')
                learned_action_applied = True
            elif learned_action == 'isolate_host' and 'isolate_host' not in actions:
                actions.append('isolate_host')
                learned_action_applied = True
            elif learned_action == 'allow':
                actions = ['log']
                risk_level = 'low'
                learned_action_applied = True
        
        return {
            'threat_detected': True,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'actions': actions,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'learned_action_applied': learned_action_applied
        }
    
    def _calculate_risk_level(self, risk_score):
        """Calculate risk level"""
        for level, (min_score, max_score) in self.risk_levels.items():
            if min_score <= risk_score < max_score:
                return level
        return 'high'