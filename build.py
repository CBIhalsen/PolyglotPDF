# import os
# import sys
# import platform
# import subprocess
# import shutil
# from pathlib import Path
#
# def main():
#     #────────────────────────────────────────────────────────────────────────
#     # 1. 准备工作：获取当前目录、检查 PyInstaller
#     #────────────────────────────────────────────────────────────────────────
#     current_dir = Path(__file__).parent.absolute()
#     print(f"当前目录: {current_dir}")
#
#     try:
#         import PyInstaller
#         print("PyInstaller 已安装")
#     except ImportError:
#         print("安装 PyInstaller...")
#         subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
#
#     system = platform.system().lower()
#     print(f"当前系统: {system}")
#
#     # 设置路径分隔符 (Windows 下为 ;，其他平台为 :)
#     separator = ';' if system == 'windows' else ':'
#
#     # 生成可执行文件名称 (Windows 上会变成 EbookTranslator.exe，其它系统就没有后缀)
#     exe_name = "EbookTranslator"
#
#     #────────────────────────────────────────────────────────────────────────
#     # 2. 创建输出目录（供后面使用，onedir 模式下可自由放置打包产物）
#     #────────────────────────────────────────────────────────────────────────
#     dist_app_dir = current_dir / "dist" / exe_name
#     os.makedirs(dist_app_dir, exist_ok=True)
#
#     #────────────────────────────────────────────────────────────────────────
#     # 3. 根据你的需要，检查关键资源文件
#     #────────────────────────────────────────────────────────────────────────
#     required_files = {
#         'app.py': True,
#         'index.html': True,
#         'config.json': True,
#         'static': True,
#         'recent.json': True
#     }
#     for file_name, required in required_files.items():
#         file_path = current_dir / file_name
#         if not file_path.exists() and required:
#             print(f"错误: 必要文件 '{file_name}' 不存在")
#             sys.exit(1)
#
#     #────────────────────────────────────────────────────────────────────────
#     # 4. 构建 PyInstaller 的命令
#     #    使用 --onedir 模式，并设置可执行文件名称为 EbookTranslator
#     #────────────────────────────────────────────────────────────────────────
#     pyinstaller_cmd = [
#         sys.executable, '-m', 'PyInstaller',
#         '--noconfirm',
#         '--onedir',          # onedir 模式
#         '--name', exe_name   # 生成文件(文件夹)名
#     ]
#
#     # 如果在 Windows 平台，并且有 icon.ico，就使用图标
#     icon_file = current_dir / "icon.ico"
#     if system == 'windows' and icon_file.exists():
#         pyinstaller_cmd.extend(["--icon", str(icon_file)])
#
#     #────────────────────────────────────────────────────────────────────────
#     # 5. 设置 --add-data 参数，打包静态资源与需要的文件
#     #────────────────────────────────────────────────────────────────────────
#     data_files = []
#     if (current_dir / 'static').exists():
#         data_files.append((str(current_dir / 'static'), 'static'))
#     if (current_dir / 'index.html').exists():
#         data_files.append((str(current_dir / 'index.html'), '.'))
#     if (current_dir / 'config.json').exists():
#         data_files.append((str(current_dir / 'config.json'), '.'))
#     if (current_dir / 'recent.json').exists():
#         data_files.append((str(current_dir / 'recent.json'), '.'))
#
#     for src, dst in data_files:
#         pyinstaller_cmd.extend(['--add-data', f"{src}{separator}{dst}"])
#
#     # 最后指定主脚本（app.py）
#     pyinstaller_cmd.append(str(current_dir / 'app.py'))
#
#     #────────────────────────────────────────────────────────────────────────
#     # 6. 打印并执行命令
#     #────────────────────────────────────────────────────────────────────────
#     print("执行 PyInstaller 命令:\n", " ".join(map(str, pyinstaller_cmd)))
#     try:
#         subprocess.run(pyinstaller_cmd, check=True)
#         print("PyInstaller 打包完成")
#     except Exception as e:
#         print(f"PyInstaller 打包失败: {e}")
#         sys.exit(1)
#
#     #────────────────────────────────────────────────────────────────────────
#     # 7. 打包完成后，一般会在 dist/EbookTranslator 目录下看到:
#     #    ├─ EbookTranslator.exe (Windows) 或 EbookTranslator(其它系统)
#     #    ├─ 静态资源、依赖库、.. 等文件
#     #────────────────────────────────────────────────────────────────────────
#     build_dir = current_dir / "build"
#     spec_file = current_dir / f"{exe_name}.spec"
#
#     # 清理临时文件
#     if build_dir.exists():
#         shutil.rmtree(build_dir)
#     if spec_file.exists():
#         spec_file.unlink()
#
#     print("Flask 应用打包完成！\n请查看 dist/EbookTranslator 文件夹，"
#           "其中的 EbookTranslator.exe(Windows) 或 EbookTranslator(其他平台) 即可运行。")
#
#
# if __name__ == "__main__":
#     main()


import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def main():
    # ────────────────────────────────────────────────────────────────────────
    # 1. 准备工作：获取当前目录、检查 PyInstaller
    # ────────────────────────────────────────────────────────────────────────
    current_dir = Path(__file__).parent.absolute()
    print(f"当前目录: {current_dir}")

    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    system = platform.system().lower()
    print(f"当前系统: {system}")

    # 生成可执行文件名称 (Windows 上会变成 EbookTranslator.exe，其它系统就没有后缀)
    exe_name = "EbookTranslator"

    # ────────────────────────────────────────────────────────────────────────
    # 2. 创建输出目录
    # ────────────────────────────────────────────────────────────────────────
    dist_dir = current_dir / "dist"
    dist_app_dir = dist_dir / exe_name

    # 如果已存在，先删除
    if dist_app_dir.exists():
        print(f"清理已存在的输出目录: {dist_app_dir}")
        shutil.rmtree(dist_app_dir)

    os.makedirs(dist_app_dir, exist_ok=True)

    # ────────────────────────────────────────────────────────────────────────
    # 3. 检查关键资源文件
    # ────────────────────────────────────────────────────────────────────────
    required_files = {
        'app.py': True,
        'index.html': True,
        'pdfviewer.html': True,
        'pdfviewer2.html': True,  
        'merge_pdf.py': True,     
        'config.json': True,
        'static': True
    }
    for file_name, required in required_files.items():
        file_path = current_dir / file_name
        if not file_path.exists() and required:
            print(f"错误: 必要文件 '{file_name}' 不存在")
            sys.exit(1)

    # ────────────────────────────────────────────────────────────────────────
    # 4. 构建 PyInstaller 的命令 - 不添加任何资源文件
    # ────────────────────────────────────────────────────────────────────────
    pyinstaller_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--onedir',  # onedir 模式
        '--name', exe_name,  # 生成文件(文件夹)名
        ##'--windowed'  # 生成 macOS 的 .app 文件
    ]

    # 如果在 Windows 平台，并且有 icon.ico，就使用图标
    icon_file = current_dir / "icon.ico"
    if system == 'windows' and icon_file.exists():
        pyinstaller_cmd.extend(["--icon", str(icon_file)])

    # 最后指定主脚本（app.py）
    pyinstaller_cmd.append(str(current_dir / 'app.py'))

    # ────────────────────────────────────────────────────────────────────────
    # 5. 执行 PyInstaller 命令
    # ────────────────────────────────────────────────────────────────────────
    print("执行 PyInstaller 命令:\n", " ".join(map(str, pyinstaller_cmd)))
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("PyInstaller 打包完成")
    except Exception as e:
        print(f"PyInstaller 打包失败: {e}")
        sys.exit(1)

    # ────────────────────────────────────────────────────────────────────────
    # 6. 手动复制所有资源文件到输出目录
    # ────────────────────────────────────────────────────────────────────────
    print("\n开始复制资源文件到输出目录...")

    # 复制 index.html
    if (current_dir / 'index.html').exists():
        print(f"复制 index.html 到 {dist_app_dir}")
        shutil.copy2(current_dir / 'index.html', dist_app_dir / 'index.html')


    if (current_dir / 'pdfviewer.html').exists():
        print(f"复制 pdfviewer.html 到 {dist_app_dir}")
        shutil.copy2(current_dir / 'pdfviewer.html', dist_app_dir / 'pdfviewer.html')
        
    # 复制 pdfviewer2.html 
    if (current_dir / 'pdfviewer2.html').exists():
        print(f"复制 pdfviewer2.html 到 {dist_app_dir}")
        shutil.copy2(current_dir / 'pdfviewer2.html', dist_app_dir / 'pdfviewer2.html')
        
    # 复制 merge_pdf.py 
    if (current_dir / 'merge_pdf.py').exists():
        print(f"复制 merge_pdf.py 到 {dist_app_dir}")
        shutil.copy2(current_dir / 'merge_pdf.py', dist_app_dir / 'merge_pdf.py')
        
    # 复制 config.json
    if (current_dir / 'config.json').exists():
        print(f"复制 config.json 到 {dist_app_dir}")
        shutil.copy2(current_dir / 'config.json', dist_app_dir / 'config.json')

    # 复制 recent.json (如果存在)
    if (current_dir / 'recent.json').exists():
        print(f"复制 recent.json 到 {dist_app_dir}")
        shutil.copy2(current_dir / 'recent.json', dist_app_dir / 'recent.json')

    # 复制 static 目录
    if (current_dir / 'static').exists():
        static_dest = dist_app_dir / 'static'
        print(f"复制 static 目录到 {static_dest}")
        if static_dest.exists():
            shutil.rmtree(static_dest)
        shutil.copytree(current_dir / 'static', static_dest)

    # 复制其他可能需要的文件
    other_files = ['README.md', 'LICENSE', 'requirements.txt']
    for file_name in other_files:
        if (current_dir / file_name).exists():
            print(f"复制 {file_name} 到 {dist_app_dir}")
            shutil.copy2(current_dir / file_name, dist_app_dir / file_name)

    # ────────────────────────────────────────────────────────────────────────
    # 7. 清理临时文件
    # ────────────────────────────────────────────────────────────────────────
    build_dir = current_dir / "build"
    spec_file = current_dir / f"{exe_name}.spec"

    if build_dir.exists():
        print(f"清理 build 目录: {build_dir}")
        shutil.rmtree(build_dir)
    if spec_file.exists():
        print(f"删除 spec 文件: {spec_file}")
        spec_file.unlink()

    # ────────────────────────────────────────────────────────────────────────
    # 8. 完成
    # ────────────────────────────────────────────────────────────────────────
    print("\n打包完成！")
    print(f"应用程序位于: {dist_app_dir}")
    print(f"可执行文件: {dist_app_dir / exe_name}{'.exe' if system == 'windows' else ''}")
    print("所有资源文件已直接复制到输出目录，可以直接查看和编辑。")


if __name__ == "__main__":
    main()