import sys
import jmcomic

try:
  album_id_str  = sys.argv[1]
  album_id = int(album_id_str.strip('#'))
  option = jmcomic.create_option_by_file('./option.yml')
  jmcomic.download_album(album_id, option)
  print("OK!")
except IndexError:
  print("请在命令行中提供 album_id，例如: python app.py 422866")
except Exception as e:
  print(f"加载配置文件失败: {e}")