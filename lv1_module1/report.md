# 1. 배달 로봇의 연산 분담과 실시간성 설계

## 사용되는 하드웨어
- 2D LiDAR(15Hz)
- RGB 카메라(60 fps, 720p)
- IMU(400Hz)
- 바퀴 엔코더(2KHz)
- 모터 드라이버
- LTE 모듈(핑 1\~5ms 업로드 및 다운로드 속도 95\~100Mbps)

## 문제 1-1. 이 배달 로봇이 하는 작업의 배치표
| 작업 | 처리할 플랫폼 | 지연 예산 | 데이터량 | 근거
| :---: | :----------: | :---: | :---: | :---: |
| 모터 속도 제어 | 임베디드 | 1.5ms | 엔코더 센서 초당 처리량 16kb/s + 명령 하나당 1.5ms | 클라우드 왕복통신으로 처리시 LTE 핑 1~5ms에 처리 지연을 더해도 약 5 ~ 10ms 정도가 나오는데 예산의 3 ~ 7배 정도이므로 사용할 수 없다. 임베디드 컴퓨터의 경우 로컬제어로 1.2ms 정도로 예산 이내이기 때문에 바람직하다. |
| 장애물 감지 | Edge AI | 300ms | LiDAR 센서 초당 처리량 60kb/s + 라즈베리 파이 | 로봇의 평균 이동속도를 6km/h라고 가정할때, 시스템의 지연시간이 0.3초라고 가정하면 필요 안전거리는 1.15m로 계산된다. LiDAR 센서의 유효 감지거리는 수 m정도의 마진을 가지기 때문에 2초 ~ 3초의 지연은 커버하기에 충분할것이라고 예상되어 라즈베리파이에서 처리하는것이 바람직할것이라고 예상된다.|
| 보행자 인식 | Edge AI | 400ms | Raw 데이터량 2.76 x 60fps ≈ 166MB/s -> 압축하여 16 ~ 18MB/s로 산출 | 카메라를 통해 사람인지 아닌지를 판단하고 이 상황에서 발생할 수 있는 지연을 NPU를 통해서 줄이는것이 가장 바람직한 환경설정이라고 예상된다. |
| 지도 기반 경로 계획 | 클라우드 | 1 ~ 2s | 클라우드 업로드 데이터량 = 40 ~ 50kb/s | LTE모듈의 업/다운로드 속도가 95 ~ 100Mbps, 핑도 1~5ms 수준으로 대폭 개선되어 지연을 감안하더라도 매우 여유로우며, 네트워크 불안정성에 따른 리스크도 이전보다 크게 낮아졌을것으로 예상된다.|
| 배달 완료 사진 업로드 | 클라우드 | 1 ~ 수초 | 이미지 업로드 및 다운로드 평균속도 = 95 ~ 100Mbps | 사진을 업로드하는것은 실시간으로는 사진의 용량이 크기 때문에 실시간으로는 불가능하기 때문에 클라우드 서버에서 처리가 바람직하다. |
| 운행 로그 집계 | 클라우드 | 수분 ~ 수십분 | 운행 데이터 400 ~ 1000kb/시간 | 운행 로그를 시간 단위 또는 하루 단위로 집계한다고 가정했을때, 지연 예산과 예상 데이터량을 합하면 수십 ~ 수백mb가 될것으로 예상되기 때문에 클라우드에 업로드하면서 처리하는것이 바람직하다고 예상된다. |

## 문제 1-2. 카메라 원시 영상 전송량
압축을 하지않은 raw파일을 그대로 전송한다고 가정하였을때 :

```
초당 데이터량 = 가로 픽셀수 x 세로 픽셀수 x 채널수(RGB이므로 3채널) x 채널당 바이트수 x fps
		   = 1280 x 720 x 3 x 8 x 60
           = 1327104000 = 1.33Gbps
```

결론적으로 압축없는 데이터를 전송하려면 초당 약 166mb가 필요하다.

이 로봇에 탑재된 LTE모듈의 업/다운로드 속도는 95~100Mbps 수준이다.
아무리 LTE통신환경이 좋다고 해도 약 13~14배정도 차이가 나게된다.

**이 설계가 성립하지 않는 이유는**
* 대역폭 부족 - 보내야하는 데이터의 양에 비해 속도가 많이 차이가 나게되면(약 13~14배) 업로드 지연이 계속해서 발생하게 되어 결국 서비스가 제대로 작동하지 않을 수 있을것이라고 생각된다.

* 비용 및 전력 문제 - LTE요금제를 사용한다고 가정하면 감당할 수 없는 트래픽과 요금이 발생할 것이고, 발열문제 또한 굉장히 심각할것으로 예상된다.

* 규모 확장 문제 - 한대만 운용한다면 어느정도 타협하에 운용이 가능하겠지만, N대로 늘어날경우 그에 따른 부하도 비례하여 증가할것이기 때문에 규모를 늘리는데 많은 문제가 있을것이라고 예상된다.

## 문제 1-3. 인지·판단·제어 계층 매핑과 주기표

[인지]    보행자 인식, 장애물 감지

[판단] 지도 기반 경로 계획, 글로벌/로컬 경로 계획

[제어] 모터속도 제어, 비상정지

아래 그림은 주기표를 간단하게 그린 이미지이다.

![](https://velog.velcdn.com/images/kimhwa0486/post/68799d23-9187-4796-a85a-d887300c6de2/image.png)

## 문제 1-4. Hard/Firm/Soft 분류표

| 작업 | 중요도 | 마감을 놓치면 |
| :----: | :----------: | :-------: |
| 모터 속도 제어 | Hard | 마감을 초과할경우 제어가 불안정해져 하드웨어의 파손으로 이어질 수 있다. |
| 장애물 감지 | Hard | 마감을 초과할경우 장애물과 충돌할 위험이 있다. |
| 보행자 인식 | firm | 마감을 초과할경우 늦게 들어온 프레임은 사용하지 않고 최신의 프레임을 사용하여 판단한다. |
| 지도 기반 경로 계획 | soft | 마감을 초과할경우 이전에 사용하던 경로를 계속 사용하여 주행가능하다. |
| 배달 완료 사진 업로드 | soft | 마감을 초과할경우 업로드 완료까지 대기해도 치명적 오류가 발생하지 않는다. |
| 운행 로그 집계 | soft | 마감을 초과할경우 집계에 지연이 생기지만 왜곡이나 깨짐이 발생하지 않는다. |



## 문제 1-5. 주기 · 지연 · 지터 구분
* 주기 : LiDAR센서의 스캔 주기, RGB카메라의 촬영주기

* 지연 : 배달로봇이 장애물을 인식하고 속도를 줄이기위해 통신하는 과정에서 발생하는 지연

* 지터 : LTE통신환경의 불규칙함으로 인한 로봇의 속도 불안정함

# 2. 원격 접속(SSH)과 센서 장치 경로 고정

## 문제 2-1. 고른 접속 대상
접속 대상 : localhost

```bash
터미널 입력

ssh pa16@localhost

실행결과

The authenticity of host 'localhost (127.0.0.1)' can't be established.
ED25519 key fingerprint is SHA256:yb+LbFitA4aX/ZzX+xM263X3FmTVgcJ58oY5dwHPR2c.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'localhost' (ED25519) to the list of known hosts.
pa16@localhost's password: 
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.8.0-138-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

1 device has a firmware upgrade available.
Run `fwupdmgr get-upgrades` for more information.


Applications를 위한 확장된 보안 유지보수 비활성화됨.

2개의 업데이트가 즉시 적용 가능합니다.
추가 업데이트를 확인하려면 apt list --upgradable 을 실행하세요.

146 추가 보안 업데이트는 ESM Apps에 적용될 수 있습니다. 
ESM Apps 서비스 at https://ubuntu.com/esm 활성화에 대해 자세히 알아보십시오.


The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.


1 device has a firmware upgrade available.
Run `fwupdmgr get-upgrades` for more information.
```

```bash
who

pa16     tty2         2026-08-25 08:54 (tty2)
pa16     pts/3        2026-08-25 09:32 (127.0.0.1)
pa16     pts/5        2026-08-25 09:52 (127.0.0.1)
```

```bash
echo &SSH_CONNECTION

127.0.0.1 53476 127.0.0.1 22

```

## 문제 2-2. 개인키·공개키 중 서버에 등록하는 것


```bash
pa16@pa16-Legion-Pro-5-16IAX10:/$ ls -al ~/.ssh
합계 36
drwx------  2 pa16 pa16 4096 Aug 25 09:51 .
drwxr-x--- 33 pa16 pa16 4096 Aug 25 16:11 ..
-rw-------  1 pa16 pa16  696 Aug 25 09:51 authorized_keys
-rw-------  1 pa16 pa16  432 Aug 25 09:49 id_ed25519
-rw-r--r--  1 pa16 pa16  112 Aug 25 09:49 id_ed25519.pub
-rw-------  1 pa16 pa16 2622 Aug  7 12:49 id_rsa
-rw-r--r--  1 pa16 pa16  584 Aug  7 12:49 id_rsa.pub
-rw-------  1 pa16 pa16  978 Aug 25 09:32 known_hosts
-rw-r--r--  1 pa16 pa16  142 Aug 25 09:32 known_hosts.old
```

터미널에서 8월 25일에 생성한 키쌍을 확인할 수 있다.
이때 .pub으로 끝나는것이 공개키인데 이 공개키를 서버에 등록해야 한다.

공개키는 계좌번호와 같이 누구나 가질 수 있지만 나만 가질 수 있는 고유한 번호가 되기 때문이다.
하지만 개인키는 비밀번호와 같은 것이기 때문에 절대 공개해서는 안된다.

## 문제 2-3. 원격 단일 명령 실행과 scp전송 출력

```bash
who

pa16     tty2         2026-08-25 08:54 (tty2)
pa16     pts/3        2026-08-25 09:32 (127.0.0.1)
pa16     pts/5        2026-08-25 09:52 (127.0.0.1)
```

```bash
echo &SSH_CONNECTION

127.0.0.1 53476 127.0.0.1 22

```

```bash
pa16@pa16-Legion-Pro-5-16IAX10:/$ ssh pa16@localhost 'uname -a'

Linux pa16-Legion-Pro-5-16IAX10 6.8.0-138-generic #138~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Aug  7 13:43:15 UTC  x86_64 x86_64 x86_64 GNU/Linux
```

## 문제 2-4. 가상의 센서(LiDAR, IMU)를 만들고, 두 장치를 구분하는 속성

두 장치를 구분할 수 있는 속성을 모두 찾아 아래에 표로 정리하였다.

| 항목 | loop23 | loop24 |
| :----: | :-----: | :-------: |
| devpath | .../block/loop23 | .../block/loop24 |
| KERNEL | "loop23" | "loop24" |
| ATTR{diskseq} | "51" | "53" |

* devpath는 서로 다른 가상센서이기 때문에 당연히 다르다.

* KERNEL은 터미널에서 센서를 지칭하는 명칭이 다름을 나타내준다.

* ATTR{diskseq}는 센서에 할당된 디스크 순번을 의미하는데 각각 51번째, 53번째의 순번이 배정되었다는 의미이다.

## 문제 2-5. udev 규칙 2개 + 규칙 키 설명표
* SUBSYSTEM=="block", KERNEL=="loop*", ATTR{loop/backing_file}=="*/lidar.img", SYMLINK+="robot_lidar"

* SUBSYSTEM=="block", KERNEL=="loop*", ATTR{loop/backing_file}=="*/imu.img", SYMLINK+="robot_imu"


## +근거

`losetup -f`로 생성한 loop 장치(`lidar.img`, `imu.img`)는 **가상 블록 디바이스**로, `SUBSYSTEM=="usb"`가 아닌 `SUBSYSTEM=="block"`에 속한다. 따라서 idVendor/idProduct 같은 USB 디스크립터 속성은 존재하지 않으며, 대신 이 장치가 어떤 파일을 물고 있는지를 나타내는 `ATTR{loop/backing_file}` 속성으로 장치를 식별해야 하는것이 맞을것 같다고 판단하였다.

## +규칙 키 설명표

| 키 (Key) | 연산자 | 값 (예시) | 역할 |
|:---:|:---:|:---:|:---:|
| `SUBSYSTEM` | `==` | `"block"` | 이 장치가 속한 커널 서브시스템을 지정. block 서브시스템(디스크, loop 장치 등)에서 발생하는 이벤트만 이 규칙의 대상으로 삼음 |
| `KERNEL` | `==` | `"loop*"` | 커널이 붙인 장치 이름 패턴. `loop0`, `loop21` 등 loop로 시작하는 모든 이름을 매칭 (번호는 매번 바뀔 수 있으므로 와일드카드 사용) |
| `ATTR{loop/backing_file}` | `==` | `"*/lidar.img"` | 이 loop 장치가 실제로 연결(attach)하고 있는 원본 파일의 경로. sysfs 속성(`/sys/class/block/loopN/loop/backing_file`)을 조회해 비교. 앞부분 경로는 환경마다 다를 수 있어 `*`로 와일드카드 처리하고, 파일명만 고정 매칭 |
| `SYMLINK` | `+=` | `"robot_lidar"` | 매칭된 장치에 대해 `/dev/` 아래 별칭(심볼릭 링크)을 생성. `+=`이므로 기존 이름(`/dev/loop21` 등)은 유지한 채 새 이름만 추가됨 |



## 문제 2-6. 순서를 바꿔 재연결한 후 결과
```bash
pa16@pa16-Legion-Pro-5-16IAX10:~/fake_sensors$ sudo losetup -d /dev/loop21
[sudo] pa16 암호: 

pa16@pa16-Legion-Pro-5-16IAX10:~/fake_sensors$ sudo losetup -d /dev/loop22

pa16@pa16-Legion-Pro-5-16IAX10:~/fake_sensors$ sudo losetup -f --show /home/pa16/fake_sensors/imu.img 
/dev/loop21

pa16@pa16-Legion-Pro-5-16IAX10:~/fake_sensors$ sudo losetup -f --show /home/pa16/fake_sensors/lidar.img 
/dev/loop22

pa16@pa16-Legion-Pro-5-16IAX10:~/fake_sensors$ ls -l /dev/robot_lidar /dev/robot_imu 
lrwxrwxrwx 1 root root 6 Aug 25 18:06 /dev/robot_imu -> loop21
lrwxrwxrwx 1 root root 6 Aug 25 18:06 /dev/robot_lidar -> loop22
```

순서를 바꾼뒤에 재연결해도 여전히 배정된 루프에 rules파일에서 설정했던 이름이 잘 출력되는것을 확인할 수 있다.

## 문제 2-7. 실제 USB 센서용 규칙 초안과 구분 근거
```bash
# LiDAR
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="robot_lidar"

# IMU
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", SYMLINK+="robot_imu"
```

만약 idVendor가 같고 idProduct만 다른 상황이라면 공급한 회사는 같은데 서로 다른 센서를 사용하는 경우를 의미한다. 이 경우에는 rules파일을 만들때 서로 구별을 할 수 있는 요소를 하나 추가해줘야 한다. 

가장 안정적이라고 생각하는 방법은 칩의 고유 형번을 추가하는것이다. 생산할때 새겨지는 고유번호이기 때문에 서로 중복될일이 절대없기 때문이다.

# 3. 팀 저장소 협업 - 브랜치·충돌 해결·PR 리뷰
## 문제 3-1. 저장소 URL/PR URL
저장소 URL : https://github.com/SangHwaKim09/team_activity_practice.git

PR URL : /images 디렉토리에 이미지로 첨부
## 문제 3-3. 충돌이 난 파일과 줄
```bash
## 배달로봇 사양
<<<<<<< HEAD
- 2D LiDAR(15Hz, 최대 감지거리 12m)
=======
- 2D LiDAR(15Hz, 360도)
>>>>>>> branch-b
- RGB 카메라(60 fps, 720p)
- IMU(400Hz)
- 바퀴 엔코더(2KHz)
- 모터 드라이버
- LTE 모듈(핑 1\~5ms 업로드 및 다운로드 속도 95\~100Mbps)
```
<<<<<<HEAD : 현재 브랜치의 내용 시작
====== : 두 버전의 분기점 

>>>>>>>branch-b : 겹치는 다른 브랜치의 내용

```bash
자동 병합: README.md
충돌 (내용): README.md에 병합 충돌
자동 병합이 실패했습니다. 충돌을 바로잡고 결과물을 커밋하십시오.
```
## 문제 3-4. merge 방식 이력 그래프 / rebase 방식 이력 그래프

**변경후 branch 결과**
*   84594fb (HEAD -> main, origin/main, origin/HEAD) Merge branch 'branch-b'
|\  
| * 82ce6a4 (branch-b) docs: LiDAR 스캔 범위 명시
* | 7ad10b4 (branch-a) docs: LiDAR 감지거리 명시
|/  
*   670dc49 변경사항 반영
|\  
| * 2c32054 (origin/feature/compute-layout, feature/compute-layout) fix: 사진진 업로드 지연시간 정형화된 수치로 수정
| * 9372ef5 docs: 연산 분담 설계 문서 추가
| * bf877be docs: 연산 분담 설계 문서 추가
|/  
* 1329be6 docs: LTE 모듈 표기 수정
* 0574e2b docs: 배달 로봇 사양 추가
* e00b906 README.md 추가
* 44cd431 Initial commit

**rebase후 branch 결과**
* 3f9d1f3 (HEAD -> main, origin/main, origin/feature/udev-rules, origin/HEAD, feature/udev-rules) docs: udev 규칙 파일 및 키 설명표 추가
*   84594fb Merge branch 'branch-b'
|\  
| * 82ce6a4 (branch-b) docs: LiDAR 스캔 범위 명시
* | 7ad10b4 (branch-a) docs: LiDAR 감지거리 명시
|/  
*   670dc49 변경사항 반영
|\  
| * 2c32054 (origin/feature/compute-layout, feature/compute-layout) fix: 사진진 업로드 지연시간 정형화된 수치로 수정
| * 9372ef5 docs: 연산 분담 설계 문서 추가
| * bf877be docs: 연산 분담 설계 문서 추가
|/  
* 1329be6 docs: LTE 모듈 표기 수정
* 0574e2b docs: 배달 로봇 사양 추가
* e00b906 README.md 추가
* 44cd431 Initial commit

## 문제 3-5. 언제 merge를, 언제 rebase를 쓸지(팀규칙)

- main 은 절대 rebase하지 않는다.
- feature 브랜치를 최신화할 때는 git rebase main 을 사용한다.
- PR 병합은 merge commit을 남긴다 — 언제 어떤 작업이 통합됐는지 추적하기 위해.
- 이미 공유된 브랜치는 rebase 대신 merge로 최신화한다.
- force push가 필요하면 반드시 --force-with-lease 를 쓴다.