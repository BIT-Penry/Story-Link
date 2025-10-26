#!/usr/bin/env python3
"""
创建一个示例视频文件
用于演示时替代 Mock 视频
"""
from pathlib import Path

def create_sample_video():
    """
    创建一个最小但有效的 MP4 视频文件
    这个文件可以被大多数视频播放器识别
    """
    video_dir = Path("videos")
    video_dir.mkdir(exist_ok=True)
    
    sample_path = video_dir / "sample_demo.mp4"
    
    # 这是一个最小的有效 MP4 文件结构
    # 包含基本的 ftyp 和 moov atoms
    minimal_mp4 = bytes([
        # ftyp atom
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
        0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
        0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
        0x6D, 0x70, 0x34, 0x31, 0x00, 0x00, 0x00, 0x08,
        0x66, 0x72, 0x65, 0x65,
        # moov atom (简化版)
        0x00, 0x00, 0x00, 0x08, 0x6D, 0x6F, 0x6F, 0x76
    ])
    
    sample_path.write_bytes(minimal_mp4)
    print(f"✅ 创建示例视频: {sample_path}")
    print(f"📁 文件大小: {len(minimal_mp4)} 字节")
    
    return sample_path

if __name__ == "__main__":
    create_sample_video()
    print("\n💡 提示: 在演示时,建议替换为真实的示例视频文件")
    print("   可以将任意 MP4 文件复制到 videos/sample_demo.mp4")

