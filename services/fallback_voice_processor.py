"""
Резервный процессор для обработки голосовых сообщений
"""
import os
import speech_recognition as sr
import tempfile
import subprocess

class FallbackVoiceProcessor:
    """Резервный процессор для обработки голосовых сообщений"""
    
    @staticmethod
    def process_voice_message(audio_file_path):
        """Обработка голосового сообщения с резервными методами"""
        try:
            print(f"🔄 Обработка файла: {audio_file_path}")
            
            # Проверяем существование файла
            if not os.path.exists(audio_file_path):
                print(f"❌ Файл не найден: {audio_file_path}")
                return None, "Файл не найден"
            
            print(f"✅ Файл найден, размер: {os.path.getsize(audio_file_path)} байт")
            
            # Пробуем разные методы обработки
            methods = [
                FallbackVoiceProcessor._try_ffmpeg_convert,
                FallbackVoiceProcessor._try_pydub_method,
                FallbackVoiceProcessor._try_direct_method
            ]
            
            for i, method in enumerate(methods, 1):
                print(f"🔄 Попытка {i}: {method.__name__}")
                try:
                    result = method(audio_file_path)
                    if result:
                        return result, None
                except Exception as e:
                    print(f"❌ Метод {i} не сработал: {e}")
                    continue
            
            return None, "Не удалось обработать аудиофайл"
            
        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            return None, f"Общая ошибка: {e}"
    
    @staticmethod
    def _try_ffmpeg_convert(audio_file_path):
        """Попытка конвертации через локальный FFmpeg"""
        try:
            # Проверяем наличие локального FFmpeg
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            ffmpeg_path = os.path.join(project_root, "ffmpeg", "ffmpeg.exe")
            
            if not os.path.exists(ffmpeg_path):
                print(f"❌ FFmpeg не найден: {ffmpeg_path}")
                return None
            
            # Создаем временный WAV файл
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
            
            try:
                # Конвертируем OGG в WAV
                cmd = [
                    ffmpeg_path,
                    '-i', audio_file_path,
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    wav_path
                ]
                
                print(f"🔄 Выполняем команду: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(wav_path):
                    print(f"✅ Конвертация успешна: {wav_path}")
                    return FallbackVoiceProcessor._recognize_speech(wav_path)
                else:
                    print(f"❌ Ошибка конвертации: {result.stderr}")
                    return None
                    
            finally:
                # Очистка
                if os.path.exists(wav_path):
                    try:
                        os.remove(wav_path)
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ FFmpeg метод не сработал: {e}")
            return None
    
    @staticmethod
    def _try_pydub_method(audio_file_path):
        """Попытка обработки через pydub"""
        try:
            from pydub import AudioSegment
            
            # Настраиваем пути к FFmpeg
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
            ffmpeg_path = os.path.join(project_root, "ffmpeg", "ffmpeg.exe")
            ffprobe_path = os.path.join(project_root, "ffmpeg", "ffprobe.exe")
            
            if os.path.exists(ffmpeg_path):
                AudioSegment.converter = ffmpeg_path
                AudioSegment.ffmpeg = ffmpeg_path
                print(f"✅ Используем локальный FFmpeg: {ffmpeg_path}")
            
            if os.path.exists(ffprobe_path):
                AudioSegment.ffprobe = ffprobe_path
                print(f"✅ Используем локальный FFprobe: {ffprobe_path}")
            
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_path = temp_wav.name
            
            try:
                # Загружаем аудио
                audio = AudioSegment.from_file(audio_file_path)
                print(f"✅ Аудио загружено через pydub: {len(audio)} мс")
                
                # Экспортируем в WAV
                audio.export(wav_path, format='wav')
                
                if os.path.exists(wav_path):
                    # Распознаем речь
                    return FallbackVoiceProcessor._recognize_speech(wav_path)
                else:
                    return None
                    
            finally:
                # Очистка
                if os.path.exists(wav_path):
                    try:
                        os.remove(wav_path)
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ pydub метод не сработал: {e}")
            return None
    
    @staticmethod
    def _try_direct_method(audio_file_path):
        """Попытка прямой обработки"""
        try:
            # Пробуем распознать напрямую
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_file_path) as source:
                audio_data = recognizer.record(source)
            
            recognized_text = recognizer.recognize_google(audio_data, language='ru-RU')
            print(f"✅ Прямое распознавание успешно: '{recognized_text}'")
            return recognized_text
            
        except Exception as e:
            print(f"❌ Прямой метод не сработал: {e}")
            return None
    
    @staticmethod
    def _recognize_speech(wav_path):
        """Распознавание речи из WAV файла"""
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            
            recognized_text = recognizer.recognize_google(audio_data, language='ru-RU')
            print(f"✅ Распознано: '{recognized_text}'")
            return recognized_text
            
        except sr.UnknownValueError:
            print("❌ Речь не распознана")
            return None
        except sr.RequestError as e:
            print(f"❌ Ошибка API: {e}")
            return None
        except Exception as e:
            print(f"❌ Ошибка распознавания: {e}")
            return None 