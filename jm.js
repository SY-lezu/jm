import { spawn } from "child_process"

export class JM extends plugin {
  constructor() {
    super({
      name: "jm下载",
      dsc: "jm下载",
      event: "message",
      priority: 5000,
      rule: [
        {
          /** 命令正则匹配 */
          reg: /jm\d+/i,
          /** 执行方法 */
          fnc: "Jm",
        },
      ],
    })
  }

  /** JM下载本子 */
  async Jm(e) {
    const jmId = e.msg.replace(/\/?(jm|JM)/, "").trim()
    // 获取当前运行的绝对路径
    const jmPath = `${process.cwd()}/plugins/jm-plugin`
    e.reply("开始下载，请稍等...", false, { recallMsg: 20 })
    runPythonDownload(jmId).then(async success => {
      if (success) {
        e.reply("下载完成，正在打包...\n解压密码为:tianyi", true, { recallMsg: 20 })
        const sendMsg = await e.reply(
          segment.file(jmPath + "/zip/" + jmId.replace(/#/, "") + ".zip", `${jmId}.zip`),
        )
        console.log("发送文件结果:", sendMsg)

        if (!sendMsg || sendMsg.error) {
          e.reply("文件发送失败，请更换车牌", true, { recallMsg: 20 })
          return
        }
      } else {
        e.reply("下载失败，请检查日志", true, { recallMsg: 20 })
      }
    })
  }
}

/**
 * 调用Python脚本并检测是否完成
 * @param {number|string} id - 传递给Python脚本的参数
 * @returns {Promise<boolean>} - 成功完成返回true，否则返回false
 */
function runPythonDownload(id) {
  return new Promise(resolve => {
    const pythonProcess = spawn("python", ["app.py", id], {
      cwd: `${process.cwd()}/plugins/jm-plugin`, // 设置工作目录
      encoding: "utf8",
    })

    let hasCompleted = false
    const targetString = "OK!"
    const timeoutDuration = 300000 // 5分钟

    const timeout = setTimeout(() => {
      if (!hasCompleted) {
        console.error("错误：操作超时，可能下载卡住")
        pythonProcess.kill()
      }
    }, timeoutDuration)

    pythonProcess.stdout.on("data", data => {
      const output = data.toString()
      console.log(output.trim())
      if (output.includes(targetString)) {
        hasCompleted = true
        clearTimeout(timeout)
        console.log("检测到下载完成！")
        pythonProcess.kill()
        resolve(true)
      }
    })

    pythonProcess.stderr.on("data", data => {
      console.error(`Python错误: ${data}`)
    })

    pythonProcess.on("close", () => {
      clearTimeout(timeout)
      if (!hasCompleted) {
        console.error("下载失败：未检测到完成标志")
        resolve(false)
      }
    })
  })
}
