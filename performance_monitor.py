
import os
import time
import logging
import psutil
import threading
from datetime import datetime
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, interval=60):
        """
        Initialise le moniteur de performances
        
        Args:
            interval (int): Intervalle en secondes entre chaque mesure
        """
        self.interval = interval
        self.running = False
        self.thread = None
        self.stats_history = []
        self.max_history = 60  # Garder 1 heure de données (avec intervalle de 60s)
        
        # Créer le dossier de logs s'il n'existe pas
        os.makedirs('logs', exist_ok=True)
    
    def start(self):
        """Démarre le moniteur de performances dans un thread séparé"""
        if self.running:
            logger.warning("Le moniteur de performances est déjà en cours d'exécution")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"Moniteur de performances démarré (intervalle: {self.interval}s)")
    
    def stop(self):
        """Arrête le moniteur de performances"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Moniteur de performances arrêté")
    
    def _monitor_loop(self):
        """Boucle principale du moniteur"""
        while self.running:
            try:
                stats = self._collect_stats()
                self._save_stats(stats)
                self.stats_history.append(stats)
                
                # Limiter la taille de l'historique
                if len(self.stats_history) > self.max_history:
                    self.stats_history.pop(0)
                    
                # Vérifier les seuils critiques
                self._check_thresholds(stats)
                
            except Exception as e:
                logger.error(f"Erreur lors de la collecte des métriques: {str(e)}")
                
            time.sleep(self.interval)
    
    def _collect_stats(self):
        """Collecte les statistiques système et application"""
        process = psutil.Process(os.getpid())
        
        # Statistiques de mémoire
        mem = psutil.virtual_memory()
        process_mem = process.memory_info()
        
        # Statistiques CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        process_cpu = process.cpu_percent(interval=1)
        
        # Statistiques disque
        disk = psutil.disk_usage('/')
        
        # Construire l'objet de statistiques
        stats = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_total': mem.total,
                'memory_available': mem.available,
                'memory_percent': mem.percent,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_percent': disk.percent
            },
            'process': {
                'cpu_percent': process_cpu,
                'memory_rss': process_mem.rss,
                'memory_vms': process_mem.vms,
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            }
        }
        
        return stats
    
    def _save_stats(self, stats):
        """Sauvegarde les statistiques dans un fichier"""
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"logs/performance_{date_str}.jsonl"
        
        try:
            with open(filename, 'a') as f:
                f.write(json.dumps(stats) + '\n')
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des métriques: {str(e)}")
    
    def _check_thresholds(self, stats):
        """Vérifie si les métriques dépassent des seuils critiques"""
        # Vérifier la mémoire système
        if stats['system']['memory_percent'] > 90:
            logger.warning(f"ALERTE: Utilisation mémoire système élevée: {stats['system']['memory_percent']}%")
            
        # Vérifier le CPU système
        if stats['system']['cpu_percent'] > 90:
            logger.warning(f"ALERTE: Utilisation CPU système élevée: {stats['system']['cpu_percent']}%")
            
        # Vérifier l'espace disque
        if stats['system']['disk_percent'] > 90:
            logger.warning(f"ALERTE: Espace disque faible: {stats['system']['disk_percent']}%")
            
        # Vérifier la mémoire du processus (>1GB)
        if stats['process']['memory_rss'] > 1_000_000_000:
            logger.warning(f"ALERTE: Utilisation mémoire du processus élevée: {stats['process']['memory_rss'] / 1_000_000:.2f} MB")

# Fonction pour initialiser le moniteur dans main.py
def start_monitoring():
    monitor = PerformanceMonitor(interval=60)
    monitor.start()
    return monitor
