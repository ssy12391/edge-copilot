# encoding=utf-8
# 导入需要的模块
from json import loads, dumps  # 用于处理JSON数据
from os import startfile, system  # 用于启动文件和执行系统命令
from os.path import dirname
import psutil  # 用于在新的进程中执行子程序


def terminate_processes(pid_name_parameter: str) -> None:
    """_summary_

    Returns:
        _type_: _description_
    """
    processes = psutil.pids()
    print(processes)
    for each in processes:
        if psutil.Process(pid=each).name() == pid_name_parameter:
            psutil.Process(pid=each).terminate()
        else:
            with open(
                file=rf"{dirname(p=__file__)}/process_processing.txt",
                mode="a",
                encoding="utf-8",
            ) as save_data:
                save_data.write(f"{f'{psutil.Process(pid=each).name()}':★^30}\n")
    return None


def modify_edge_browser_user_datas(
    edge_data_preference_path: str = rf"C:\Users\simon\AppData\Local\Microsoft\Edge\User Data\Default\Preferences",
    edge_data_localstate_path: str = rf"C:\Users\simon\AppData\Local\Microsoft\Edge\User Data\Local State",
    copilot_register_table: str = rf"D:/SimonPythonProject/“Copilot恢复显示”.reg",
) -> tuple:
    """
    此函数用于修改Edge浏览器的用户数据和Copilot的注册表。
    参数：
        edge_data_preference_path (str): Edge浏览器的用户偏好数据文件路径，默认为"C:/Users/ssy12/AppData/Local/Microsoft/Edge/User Data/Default/Preferences"
        edge_data_localstate_path (str): Edge浏览器的本地状态数据文件路径，默认为"C:/Users/ssy12/AppData/Local/Microsoft/Edge/User Data/Local State"
        copilot_register_table (str): Copilot的注册表文件路径，默认为"D:/SimonPythonProject/“Copilot恢复显示”.reg"
    返回值类型：元组，包含修改后的variations_country和chat_ip_eligibility_status的值
    """
    # 打开并读取Edge浏览器的本地状态数据文件
    with open(file=edge_data_localstate_path, mode="r", encoding="utf-8") as load_data:
        origninal_content = load_data.read()
    # 将读取的JSON数据转换为字典对象
    json_trans_into_dictionary_object = loads(s=origninal_content)
    # 打印修改前的variations_country的值
    print(
        "修改前——variations_country:",
        json_trans_into_dictionary_object.get("variations_country"),
    )
    # 修改variations_country的值为"US"
    json_trans_into_dictionary_object["variations_country"] = "US"
    # 打印修改后的variations_country的值
    print(
        "修改后——variations_country:",
        json_trans_into_dictionary_object.get("variations_country"),
    )
    # 将修改后的字典对象转换回JSON数据
    edge_data_localstate = dumps(obj=json_trans_into_dictionary_object)
    # 将修改后的JSON数据写回文件
    with open(file=edge_data_localstate_path, mode="w", encoding="utf-8") as save_data:
        save_data.write(edge_data_localstate)

    # 以下的操作与上面类似，只是修改的是Edge浏览器的用户偏好数据文件
    with open(file=edge_data_preference_path, mode="r", encoding="utf-8") as load_data:
        origninal_content = load_data.read()
    json_trans_into_dictionary_object = loads(s=origninal_content)
    print(
        "修改前——chat_ip_eligibility_status:",
        json_trans_into_dictionary_object.get("chat_ip_eligibility_status"),
    )
    json_trans_into_dictionary_object["chat_ip_eligibility_status"] = "true"
    print(
        "修改后——chat_ip_eligibility_status:",
        json_trans_into_dictionary_object.get("chat_ip_eligibility_status"),
    )
    edge_data_preferences = dumps(obj=json_trans_into_dictionary_object)
    with open(file=edge_data_preference_path, mode="w", encoding="utf-8") as save_data:
        save_data.write(edge_data_preferences)
    # 启动Copilot的注册表文件，以修改注册表
    startfile(copilot_register_table)

    # 返回修改后的variations_country和chat_ip_eligibility_status的值
    return json_trans_into_dictionary_object.get(
        "variations_country"
    ), json_trans_into_dictionary_object.get("chat_ip_eligibility_status")


# 如果此脚本作为主程序运行
if __name__ == "__main__":
    # 打印程序启动的信息
    print(f"{'程序启动':★^120}")
    try:
        # 尝试关闭所有正在运行的Edge浏览器进程
        terminate_processes(pid_name_parameter="msedge.exe")
    except Exception as errors_warnings:
        # 如果关闭进程时发生错误，打印错误信息，并修改Edge浏览器的用户数据和Copilot的注册表
        print(errors_warnings)
        modify_edge_browser_user_datas()
    else:
        # 如果关闭进程成功，也修改Edge浏览器的用户数据和Copilot的注册表
        modify_edge_browser_user_datas()
    finally:
        # 无论是否成功，最后都打印程序关闭的信息
        print(f"{'程序关闭':★^120}")
