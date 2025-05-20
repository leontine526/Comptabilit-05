
import os
import time
import logging
import psutil
import threading
from datetime import datetime
import json
from cache_manager import get_cache_stats

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, interval=60):
        self.interval = interval
        self.running = False
        self.thread = None
        self.stats_history = []
        self.max_history = 60
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 80,
            'disk_percent': 85
        }
        
        os.makedirs('logs', exist_ok=True)
    
    def start(self):
        if self.running:
            logger.warning("Le moniteur est déjà en cours d'exécution")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"Moniteur démarré (intervalle: {self.interval}s)")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Moniteur arrêté")
    
    def _monitor_loop(self):
        while self.running:
            try:
                stats = self._collect_stats()
                self._save_stats(stats)
                self.stats_history.append(stats)
                
                if len(self.stats_history) > self.max_history:
                    self.stats_history.pop(0)
                    
                self._check_thresholds(stats)
                
            except Exception as e:
                logger.error(f"Erreur lors de la collecte: {str(e)}")
                
            time.sleep(self.interval)
    
    def _collect_stats(self):
        process = psutil.Process(os.getpid())
        
        # Statistiques système
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Statistiques de cache
        cache_stats = get_cache_stats()
        
        # Construire l'objet de statistiques
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_total': mem.total,
                'memory_available': mem.available,
                'memory_percent': mem.percent,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_percent': disk.percent,
                'load_avg': psutil.getloadavg()
            },
            'process': {
                'cpu_percent': process.cpu_percent(interval=1),
                'memory_rss': process.memory_info().rss,
                'memory_vms': process.memory_vms,
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections()),
                'io_counters': process.io_counters()._asdict()
            },
            'cache': cache_stats
        }
        
        return stats
    
    def _save_stats(self, stats):
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"logs/performance_{date_str}.jsonl"
        
        try:
            with open(filename, 'a') as f:
                f.write(json.dumps(stats) + '\n')
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def _check_thresholds(self, stats):
        # Vérifier CPU
        if stats['system']['cpu_percent'] > self.alert_thresholds['cpu_percent']:
            logger.warning(f"ALERTE: CPU système élevé: {stats['system']['cpu_percent']}%")
            
        # Vérifier mémoire  
        if stats['system']['memory_percent'] > self.alert_thresholds['memory_percent']:
            logger.warning(f"ALERTE: Mémoire système élevée: {stats['system']['memory_percent']}%")
            
        # Vérifier disque
        if stats['system']['disk_percent'] > self.alert_thresholds['disk_percent']:
            logger.warning(f"ALERTE: Espace disque faible: {stats['system']['disk_percent']}%")
            
        # Vérifier mémoire process (>1GB)
        if stats['process']['memory_rss'] > 1_000_000_000:
            logger.warning(f"ALERTE: Mémoire processus élevée: {stats['process']['memory_rss'] / 1_000_000:.2f} MB")

# Fonction pour initialiser le moniteur
def start_monitoring(interval=60):
    monitor = PerformanceMonitor(interval=interval)
    monitor.start()
    return monitor
