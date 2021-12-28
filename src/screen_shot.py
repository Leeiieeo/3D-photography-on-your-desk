import cv2

video = cv2.VideoCapture("./video/5.MP4")
count = 0
task = "bottle"
print(f"frame_width: {video.get(3)}")
print(f"frame_height: {video.get(4)}")
print(f"total frame: {video.get(7)}")
if(video.isOpened()):
    while 1:
        ret, frame = video.read()
        if ret:
            cv2.namedWindow("frame", 0);
            cv2.resizeWindow('frame', 640, 480)
            cv2.imshow("frame", frame)
            keyword = cv2.waitKey(1)
            if keyword == ord('s'):  # 按s保存当前图片
                if count < 10:
                    cv2.imwrite('./'+task +'/'+task+"_0"+str(count)+".jpg", frame)
                    print(f"saving :{task}_0{count}.jpg")
                else:
                    cv2.imwrite('./'+task + '/' + task +"_" + str(count) + ".jpg", frame)
                    print(f"saving :{task}_{count}.jpg")
                count+=1
            elif keyword == ord('q'):  # 按q退出
                break
        else:
            print("video end")
            break

else:
    print("can not open file")
video.release()
cv2.destroyAllWindows()
