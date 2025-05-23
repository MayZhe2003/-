import requests
import m3u8
import ffmpeg
import os


def download_m3u8_video(m3u8_url, output_path):
    # 将temp_folder移到try块外部
    temp_folder = 'temp_video_fragments'
    
    # 添加请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    try:
        # 下载 m3u8 文件
        response = requests.get(m3u8_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        m3u8_content = response.text

        # 解析 m3u8 文件
        m3u8_obj = m3u8.loads(m3u8_content)
        
        if not m3u8_obj.segments:
            raise Exception("M3U8文件中没有找到视频片段")

        # 创建临时文件夹
        os.makedirs(temp_folder, exist_ok=True)

        # 下载视频片段
        segment_paths = []
        print("开始下载视频片段...")
        
        for i, segment in enumerate(m3u8_obj.segments):
            segment_url = segment.uri
            if not segment_url.startswith('http'):
                base_url = m3u8_url.rsplit('/', 1)[0]
                segment_url = f'{base_url}/{segment_url}'
            
            segment_path = os.path.join(temp_folder, f'segment_{i}.ts')
            segment_paths.append(segment_path)
            
            print(f"下载片段 {i+1}/{len(m3u8_obj.segments)}")
            segment_response = requests.get(segment_url, headers=headers)  # 添加headers
            segment_response.raise_for_status()
            
            with open(segment_path, 'wb') as f:
                f.write(segment_response.content)

        if not segment_paths:
            raise Exception("没有成功下载任何视频片段")

        print("开始合并视频片段...")
        
        # 使用文件列表文本文件进行合并
        list_file = os.path.join(temp_folder, 'file_list.txt')
        with open(list_file, 'w', encoding='utf-8') as f:
            for path in segment_paths:
                f.write(f"file '{path}'\n")

        # 使用 ffmpeg 合并视频片段
        ffmpeg.input(list_file, format='concat', safe=0).output(
            output_path, c='copy').overwrite_output().run(capture_stdout=True, capture_stderr=True)

        print("清理临时文件...")
        # 清理临时文件
        os.remove(list_file)
        for path in segment_paths:
            os.remove(path)
        os.rmdir(temp_folder)

        print(f'视频已成功下载并保存为: {output_path}')
        
    except requests.exceptions.RequestException as e:
        print(f'网络请求错误: {e}')
    except ffmpeg.Error as e:
        print(f'FFmpeg错误: {e.stderr.decode()}')
    except Exception as e:
        print(f'发生错误: {e}')
    finally:
        # 确保清理临时文件
        if os.path.exists(temp_folder):
            for file in os.listdir(temp_folder):
                os.remove(os.path.join(temp_folder, file))
            os.rmdir(temp_folder)


if __name__ == "__main__":
    m3u8_url = 'https://dh5.cntv.lxdns.com/asp/h5e/hls/1200/0303000a/3/default/4f187f32cc714ab5b18502ead8e7e280/1200.m3u8'  # 替换为实际的m3u8链接
    output_path = 'output_video.mp4'
    download_m3u8_video(m3u8_url, output_path)
    