import sys
import subprocess

def get_live_hardware_networks():
    networks = []
    try:
        if sys.platform.startswith("win"):
            # Real Windows CMD network hardware scanning pipeline
            cmd = "netsh wlan show networks mode=bssid"
            stdout = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            lines = stdout.split('\n')
            current_ssid, current_bssid, current_signal, current_cipher = "", "", "", ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("SSID"):
                    parts = line.split(":")
                    if len(parts) > 1: current_ssid = parts[1].strip()
                elif line.startswith("Authentication"):
                    parts = line.split(":")
                    if len(parts) > 1: current_cipher = parts[1].strip()
                elif line.startswith("BSSID 1"):
                    parts = line.split(":")
                    if len(parts) > 1: current_bssid = ":".join(parts[1:]).strip()
                elif line.startswith("Signal"):
                    parts = line.split(":")
                    if len(parts) > 1:
                        current_signal = parts[1].strip()
                        if current_ssid and current_bssid:
                            networks.append({
                                "ssid": current_ssid[:21] if current_ssid else "Hidden_SSID",
                                "bssid": current_bssid,
                                "signal": current_signal,
                                "freq": "Dynamic Link",
                                "cipher": current_cipher[:13] if current_cipher else "WPA2"
                            })
                            current_ssid, current_bssid = "", ""
        else:
            # Real Arch Linux terminal network manager hardware probing
            cmd = "nmcli -f SSID,BSSID,SIGNAL,BARS,SECURITY,CHAN dev wifi list"
            stdout = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 5:
                        networks.append({
                            "ssid": parts[0][:21] if parts[0] != "--" else "Hidden_SSID",
                            "bssid": parts[1],
                            "signal": parts[2] + "%",
                            "freq": f"CH {parts[-2]}",
                            "cipher": parts[-1][:13]
                        })
    except Exception:
        pass
        
    return networks

def analyze_best_network(networks):
    if not networks:
        return "None_Detected", "Hardware scanner returned empty set. No physical signals active."
        
    best_net = None
    max_sig = -1
    
    for net in networks:
        try:
            # Parsing real-time numeric signal values directly
            sig_val = int(net["signal"].replace("%", "").replace("dBm", "").strip())
        except Exception:
            sig_val = 0
        if sig_val > max_sig:
            max_sig = sig_val
            best_net = net
            
    if best_net:
        reason = f"Highest live signal metrics verified at {best_net['signal']} via channel {best_net['freq']}."
        return best_net["ssid"], reason
    return "None_Detected", "Hardware link scan status failed to capture stable telemetry data."

