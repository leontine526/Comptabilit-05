"""
Crée un son de notification simple pour le système.
"""
import numpy as np
from scipy.io.wavfile import write
import os

def create_notification_sound(output_path, duration=0.3, frequency=880):
    """
    Crée un son de notification simple.
    
    Args:
        output_path (str): Chemin de sortie pour le fichier WAV
        duration (float): Durée du son en secondes
        frequency (int): Fréquence du son en Hz
    """
    # Paramètres
    sample_rate = 44100  # CD quality
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # Génération du son (une note simple avec decay)
    decay = np.exp(-t * 10)
    note = 0.5 * np.sin(2 * np.pi * frequency * t) * decay
    
    # Normalisation du son
    note = note / np.max(np.abs(note))
    
    # Conversion en int16
    audio = (note * 32767).astype(np.int16)
    
    # Sauvegarde du fichier WAV
    write(output_path, sample_rate, audio)

if __name__ == "__main__":
    # Assure que le dossier existe
    os.makedirs("static/sounds", exist_ok=True)
    
    # Crée le son de notification
    create_notification_sound("static/sounds/notification.wav")
    
    print(f"Son de notification créé : static/sounds/notification.wav")