# 导入所需的库
# from distutils.util import rfc822_escape
# 
# # 用于处理邮件头部的编码
import os  # 用于操作文件系统
import sys  # 用于访问与Python解释器紧密相关的变量和函数
import json  # 用于处理JSON数据格式
import time  # 用于时间相关的操作
import signal  # 用于设置信号处理器
import psutil  # 用于获取系统运行信息

# 定义函数，获取版本和用户数据路径
def get_version_and_user_data_path():
    # 定义一个字典，存储不同操作系统下的Edge浏览器的用户数据路径
    os_and_user_data_paths = {
        'win32': {  # Windows系统
            'stable': '~/AppData/Local/Microsoft/Edge/User Data',  # 正式版
            'canary': '~/AppData/Local/Microsoft/Edge Canary/User Data',  # Canary版
            'dev': '~/AppData/Local/Microsoft/Edge Dev/User Data',  # 开发者版
            'beta': '~/AppData/Local/Microsoft/Edge Beta/User Data',  # Beta版
        },
        'linux': {  # Linux系统
            'stable': '~/.config/microsoft-edge',  # 正式版
            'canary': '~/.config/microsoft-edge-canary',  # Canary版
            'dev': '~/.config/microsoft-edge-dev',  # 开发者版
            'beta': '~/.config/microsoft-edge-beta',  # Beta版
        },
        'darwin': {  # MacOS系统
            'stable': '~/Library/Application Support/Microsoft Edge',  # 正式版
            'canary': '~/Library/Application Support/Microsoft Edge Canary',  # Canary版
            'dev': '~/Library/Application Support/Microsoft Edge Dev',  # 开发者版
            'beta': '~/Library/Application Support/Microsoft Edge Beta',  # Beta版
        },
    }

    # 遍历字典，根据当前系统类型获取对应的用户数据路径
    for platform, version_and_user_data_path in os_and_user_data_paths.items():
        available_version_and_user_data_path = {}
        if sys.platform.startswith(platform):
            for version, user_data_path in version_and_user_data_path.items():
                # 展开用户目录并转换为绝对路径
                user_data_path = os.path.abspath(os.path.expanduser(user_data_path))
                if os.path.exists(user_data_path):
                    available_version_and_user_data_path[version] = user_data_path
            return available_version_and_user_data_path

    # 如果当前系统类型不在字典中，抛出异常
    raise Exception('Unsupported platform %s' % sys.platform)

# 定义函数，关闭Edge浏览器
def shutdown_edge():
    terminated_edges = []  # 用于存储被终止的Edge浏览器进程路径
    for process in psutil.process_iter():  # 遍历所有进程
        try:
            if sys.platform == 'darwin':
                if not process.name().startswith('Microsoft Edge'):
                    continue
            elif os.path.splitext(process.name())[0] != 'msedge':
                continue
            elif not process.is_running():
                continue
            elif process.parent() is not None and process.parent().name() == process.name():
                continue
            location = process.exe()  # 获取进程的可执行文件路径
            process.kill()  # 终止进程
            terminated_edges.append(location)  # 记录被终止的进程路径
        except psutil.NoSuchProcess:
            pass
    return terminated_edges

# 定义函数，获取最后的版本
def get_last_version(user_data_path):
    last_version_file = os.path.join(user_data_path, 'Last Version')  # 构造Last Version文件的路径
    if not os.path.exists(last_version_file):  # 检查文件是否存在
        return None
    with open(last_version_file, 'r', encoding='utf-8') as fp:  # 打开文件进行读取
        return fp.read()  # 读取并返回文件内容

# 定义函数，修改本地状态
def patch_local_state(user_data_path):
    local_state_file = os.path.join(user_data_path, 'Local State')  # 构造Local State文件的路径
    if not os.path.exists(local_state_file):  # 检查文件是否存在
        print('Failed to patch Local State. File not found', local_state_file)
        return

    with open(local_state_file, 'r', encoding='utf-8') as fp:  # 打开文件进行读取
        local_state = json.load(fp)  # 读取JSON数据

    if local_state['variations_country'] != 'US':  # 检查国家代码是否为US
        local_state['variations_country'] = 'US'  # 设置国家代码为US
        with open(local_state_file, 'w', encoding='utf-8') as fp:  # 打开文件进行写入
            json.dump(local_state, fp)  # 写入修改后的JSON数据
        print('Succeeded in patching Local State')  # 输出成功信息
    else:
        print('No need to patch Local State')  # 输出无需修改信息

# 定义函数，修改偏好设置
def patch_preferences(user_data_path):
    for file in os.listdir(user_data_path):  # 遍历用户数据路径下的所有文件和文件夹
        if not os.path.isdir(file) and file != 'Default' and not file.startswith('Profile '):
            continue

        preferences_file = os.path.join(user_data_path, file, 'Preferences')  # 构造Preferences文件的路径
        with open(preferences_file, 'r', encoding='utf-8') as fp:  # 打开文件进行读取
            preferences = json.load(fp)  # 读取JSON数据

        if preferences['browser'].get('chat_ip_eligibility_status') in [None, False]:  # 检查聊天IP资格状态
            preferences['browser']['chat_ip_eligibility_status'] = True  # 设置聊天IP资格状态为True
            with open(preferences_file, 'w', encoding='utf-8') as fp:  # 打开文件进行写入
                json.dump(preferences, fp)  # 写入修改后的JSON数据
            print('Succeeded in patching Preferences of', file)  # 输出成功信息
        else:
            print('No need to patch Preferences of', file)  # 输出无需修改信息

# 主函数
def main():
    version_and_user_data_path = get_version_and_user_data_path()  # 获取版本和用户数据路径
    if len(version_and_user_data_path) == 0:  # 检查是否获取到有效的用户数据路径
        raise Exception('No available user data path found')  # 抛出异常

    terminated_edges = shutdown_edge()  # 关闭Edge浏览器
    if len(terminated_edges) > 0:
        print('Shutdown Edge')  # 输出关闭信息

    for version, user_data_path in version_and_user_data_path.items():  # 遍历所有版本和用户数据路径
        last_version = get_last_version(user_data_path)  # 获取最后的版本
        if last_version is None:  # 检查是否获取到版本信息
            print('Failed to get version. File not found', os.path.join(user_data_path, 'Last Version'))  # 输出失败信息
            continue
        main_version = int(last_version.split('.')[0])  # 解析主版本号
        print('Patching Edge', version, last_version, '"'+user_data_path+'"')  # 输出补丁信息
        if main_version == 120:
            patch_local_state(user_data_path)  # 应用本地状态补丁
        elif main_version >= 121:
            patch_preferences(user_data_path)  # 应用偏好设置补丁
        else:
            patch_local_state(user_data_path)  # 应用本地状态补丁
            patch_preferences(user_data_path)  # 应用偏好设置补丁

    if len(terminated_edges) > 0:  # 检查是否有Edge浏览器进程被终止
        print('Restart Edge')  # 输出重启信息
        for edge in terminated_edges:  # 遍历所有被终止的Edge浏览器进程
            os.popen('"%s"' % edge)  # 重启Edge浏览器

    input('Enter to continue...')  # 等待用户输入以继续

# 程序入口
if __name__ == '__main__':
    main()  # 调用主函数