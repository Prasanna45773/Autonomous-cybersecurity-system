from datetime import datetime

class ResponseAgent:
    def __init__(self, crypto_manager=None):
        self.blocked_ips = set()
        self.isolated_hosts = set()
        self.action_log = []
        
        # Cryptography integration
        self.crypto_manager = crypto_manager
        self.signature_enabled = crypto_manager is not None
        
        if self.signature_enabled:
            print("🔐 Response Agent: Digital signatures ENABLED")
    
    def execute_actions(self, decision, source_ip='unknown'):
        """Execute response actions WITH DIGITAL SIGNATURES"""
        results = []
        
        for action in decision.get('actions', []):
            result = self._execute_action(action, source_ip, decision)
            
            # SIGN ACTION for verification
            if self.signature_enabled:
                action_data = {
                    'action': action,
                    'source_ip': source_ip,
                    'timestamp': datetime.now().isoformat(),
                    'risk_level': decision.get('risk_level')
                }
                signature = self.crypto_manager.sign_action(action_data)
                result['signature'] = signature
                result['signed'] = True
            
            results.append(result)
            
        return {
            'actions_executed': results,
            'timestamp': datetime.now().isoformat(),
            'digitally_signed': self.signature_enabled
        }
    
    def _execute_action(self, action, source_ip, decision):
        """Execute individual action"""
        
        if action == 'log':
            return self._log_event(source_ip, decision)
        elif action == 'alert':
            return self._send_alert(source_ip, decision)
        elif action == 'block_ip':
            return self._block_ip(source_ip)
        elif action == 'isolate_host':
            return self._isolate_host(source_ip)
        elif action == 'rate_limit':
            return self._apply_rate_limit(source_ip)
        else:
            return {'action': action, 'status': 'unknown'}
    
    def _log_event(self, source_ip, decision):
        """Log security event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'source_ip': source_ip,
            'threat_level': decision.get('risk_level'),
            'confidence': decision.get('confidence')
        }
        self.action_log.append(log_entry)
        
        return {'action': 'log', 'status': 'success'}
    
    def _send_alert(self, source_ip, decision):
        """Send alert"""
        print(f"🚨 ALERT: Threat from {source_ip} | Risk: {decision.get('risk_level')}")
        return {'action': 'alert', 'status': 'success'}
    
    def _block_ip(self, source_ip):
        """Block IP address"""
        self.blocked_ips.add(source_ip)
        print(f"🔒 BLOCKED (Signed): {source_ip}")
        return {'action': 'block_ip', 'status': 'success', 'ip': source_ip}
    
    def _isolate_host(self, source_ip):
        """Isolate host"""
        self.isolated_hosts.add(source_ip)
        print(f"🔐 ISOLATED (Signed): {source_ip}")
        return {'action': 'isolate_host', 'status': 'success', 'ip': source_ip}
    
    def _apply_rate_limit(self, source_ip):
        """Apply rate limiting"""
        print(f"⏱️  RATE LIMITED: {source_ip}")
        return {'action': 'rate_limit', 'status': 'success'}
    
    def get_status(self):
        """Get response status"""
        return {
            'blocked_ips': list(self.blocked_ips),
            'isolated_hosts': list(self.isolated_hosts),
            'total_actions': len(self.action_log),
            'recent_actions': self.action_log[-10:],
            'signatures_enabled': self.signature_enabled
        }