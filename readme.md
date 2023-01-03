# 期末專題

## 桌面型手部辨識滑鼠

## 研究背景

> 在科技日新月異的發展下，滑鼠已經是我們日常生活中的一部分，但我們常常忽視它的重要性。
>
> 你是否曾經遇過以下問題:
>
> - 好不容易扛著筆電、充電線到學校，當你抵達教室後才發現滑鼠忘記帶過來？
>
> - 準備要進行重要的報告時，滑鼠突然失靈 / 壞掉了？
>
> 空氣滑鼠的想法就誕生了，人人有手機與筆電的現代，鏡頭的取得難度不高！
>
> 讓使用者可以利用鏡頭將手部動作載入電腦中，如滑鼠般操作> 游標是我們的目標。

## 主要功能

> 可自定義的手指按鍵
>
> 可自定義的滑鼠靈敏度
>
> 可保存的設定
>
> 特殊手勢(不同手指的排列組合)
>
## 具體實現流程

![image](demonstrate.png)

### 1. 判斷相機位置
>
> 螢幕右上方向下照
>
> 手部右側
>
> 手部前方
>
### 2. 判斷移動狀態
>
> 高速
>
> 低速
>
> 停止
>
### 3. 判斷手指具體狀態
>
> Yolo 具體標籤:
>
> - 五指伸、屈 * 10
>
> - 握拳
>
> - 翻掌
>
### 4. Tkinter UI

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/9G_8oT0Nh8I/0.jpg)](https://www.youtube.com/watch?v=9G_8oT0Nh8I)

## 組員

- S0954001 龔品宇
- S0954005 林昀佑
- S0954022 林煜宸
- S0954040 吳季旻
- S0963032 許家碩

>
> 參考連結
>
> <https://teachablemachine.withgoogle.com/train>
>
> <https://blog.gtwang.org/programming/opencv-webcam-video-capture-and-file-write-tutorial/>
>
> <https://ithelp.ithome.com.tw/articles/10265041>
>
> <https://medium.com/%E9%9B%9E%E9%9B%9E%E8%88%87%E5%85%94%E5%85%94%E7%9A%84%E5%B7%A5%E7%A8%8B%E4%B8%96%E7%95%8C/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-ml-note-yolo-%E5%88%A9%E7%94%A8%E5%BD%B1%E5%83%8F%E8%BE%A8%E8%AD%98%E5%81%9A%E7%89%A9%E4%BB%B6%E5%81%B5%E6%B8%AC-object-detection-%E7%9A%84%E6%8A%80%E8%A1%93-3ad34a4cac70>
>
