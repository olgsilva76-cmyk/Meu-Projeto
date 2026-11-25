import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import render, cv2, numpy as np
ts=[float(x) for x in sys.argv[1:]]
ims=[]
for t in ts:
    for s in render.SH: s.close()
    t0=time.time(); f=render.frame(int(round(t*30))); print(t, round(time.time()-t0,2))
    f=cv2.resize(f,(360,640)); cv2.putText(f,f"{t:.2f}",(8,24),0,0.7,(0,255,255),2); ims.append(f)
rows=[np.hstack(ims[i:i+6]+[np.zeros_like(ims[0])]*(6-len(ims[i:i+6]))) for i in range(0,len(ims),6)]
cv2.imwrite('stills/s.jpg',np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,85])
