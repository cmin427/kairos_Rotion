
#include <Servo.h>
#include <stdlib.h>
#include <SoftwareSerial.h>




Servo base;
Servo shoulder1;
Servo shoulder2;
Servo elbow;
Servo wrist;
Servo finger;




SoftwareSerial mySerial(2,3); //rx, tx 





void slow_write_to_servo(Servo &base,Servo &shoulder1, Servo &shoulder2, Servo &elbow, Servo &wrist,Servo &gripper,int* targetAngle){

  int a1=targetAngle[0];
  int a2=targetAngle[1];
  int a3=targetAngle[2];
  int a4=targetAngle[3];
  int a5=targetAngle[4];

  

  int base_current;
  int shoulder1_current;
  int elbow_current;
  int wrist_current;
  int gripper_current;

    base_current=base.read();
    shoulder1_current=shoulder1.read();
    elbow_current=elbow.read();
    wrist_current=wrist.read();
    gripper_current=gripper.read();


    if(a1==-1){
    a1=base_current;
    }
    if(a2==-1){
    a2=shoulder1_current;
    }
    if(a3==-1){
    a3=shoulder2_current;
    }
    if(a4==-1){
    a4=wrist_current;
    }
    if(a5==-1){
    a5=gripper_current;
    }

  while(1){
    base_current=base.read();
    shoulder1_current=shoulder1.read();
    elbow_current=elbow.read();
    wrist_current=wrist.read();
    gripper_current=gripper.read();



    //모터 1 제어
    if(base_current>a1){
      base_current--;
      base.write(base_current);
      // Serial.println(base_current-a1);
      delay(25);
    }
    else if(base_current<a1){
      base_current++;
      base.write(base_current);
      delay(25);
    }

    //모터 숄더2개  제어
    if((a2>=0)&&(a2<=175)){
      int shoulder2_current;
      
    if(shoulder1_current>a2){
      shoulder1_current--;
      shoulder2_current = shoulder1_current+7;
      shoulder1.write(shoulder1_current);
      shoulder2.write(shoulder2_current);
      delay(25);
    }
    else if(shoulder1_current<a2){
      shoulder1_current++;
      shoulder2_current = shoulder1_current+7;
      shoulder1.write(shoulder1_current);
      shoulder2.write(shoulder2_current);
      delay(25);
    }
    }


    //모터 4 제어 
    if(elbow_current>a3){
      elbow_current--;
      elbow.write(elbow_current);
      delay(25);
    }
    else if(elbow_current<a3){
      elbow_current++;
      elbow.write(elbow_current);
      delay(25);
    }

    //모터 5 제어 
    if(wrist_current>a4){
      wrist_current--;
      wrist.write(wrist_current);
      delay(25);
    }
    else if(wrist_current<a4){
      wrist_current++;
      wrist.write(wrist_current);
      delay(25);
    }
    if(gripper_current>a5){
      gripper_current--;
      gripper.write(gripper_current);
      delay(25);
    }
    else if(gripper_current<a5){
      gripper_current++;
      gripper.write(gripper_current);
      delay(25);
    }
    if((base_current==a1) && (shoulder1_current==a2) && (elbow_current==a3) && (wrist_current==a4)&& (gripper_current==a5)){
      break;
    }
  }

  Serial.println("done angle write");
  Serial.println(base_current);
  Serial.println(shoulder1_current);
  Serial.println(elbow_current);
  Serial.println(wrist_current);
  Serial.println(gripper_current);
}


String waitUntilAngleInput(SoftwareSerial &mySerial){
  // 라즈베리파이가 각 보냄 
  // checksum 계산해서 정합성 체크함
  // 맞으면 valid 보내고 각으로 취급함 
  // 틀리면 재전송 요청함 
  // 
  

  mySerial.flush();
  Serial.println("waiting for serial input \n");
  unsigned long previousMillis =millis();
  while(!mySerial.available()){

    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= 5000) {
      Serial.println("waiting for serial input");
      previousMillis = currentMillis;
    }

    delay(500);
  }

  String receive_from_rasberry=mySerial.readStringUntil('\n');
  return receive_from_rasberry;
}

void sendInvalidMesg(SoftwareSerial &mySerial){
  mySerial.write("invalid");
}

void sendDoneMesg(SoftwareSerial &mySerial){
  mySerial.write("DONE");
}

bool checkSumValidity(String text) {
  // '|' 문자의 위치를 찾기
  int index_of_bar = text.indexOf('|');
  
  // '|' 문자가 없다면 유효하지 않음
  if (index_of_bar == -1) {
    return false;
  }

  // 데이터를 '|' 기준으로 분리
  String data = text.substring(0, index_of_bar);
  String checkSumStr = text.substring(index_of_bar + 1);

  // 문자열을 숫자로 변환 (체크섬 값)
  int checkSum = checkSumStr.toInt();
  
  // 체크섬 변환이 실패한 경우 (숫자가 아닌 경우)
  if (checkSum == 0 && checkSumStr != "0") {
    return false;
  }

  // 체크섬 계산
  int sum = 0;
  for (int i = 0; i < data.length(); i++) {
    sum += data[i];  // 각 문자(아스키 코드 값)의 합을 구함
  }

  // 256으로 나눈 나머지가 체크섬 값과 동일한지 확인
  if (sum % 256 != checkSum) {
    return false;
  }

  return true;  // 체크섬이 일치하면 true 리턴
}

int* parse_abcd_str(String receive_from_rasberry){

  static int intArray[5];

  int a_index=receive_from_rasberry.indexOf('a');
  int b_index=receive_from_rasberry.indexOf('b');
  int c_index=receive_from_rasberry.indexOf('c');
  int d_index=receive_from_rasberry.indexOf('d');
  int e_index=receive_from_rasberry.indexOf('e');
  int f_index=receive_from_rasberry.indexOf('f');


  //abcde 사이 숫자 스트링으로 추출
  String j1_str=receive_from_rasberry.substring(a_index+1,b_index);
  String j2_str=receive_from_rasberry.substring(b_index+1,c_index);
  String j3_str=receive_from_rasberry.substring(c_index+1,d_index);
  String j4_str=receive_from_rasberry.substring(d_index+1,e_index);
  String gripper_str=receive_from_rasberry.substring(e_index+1,f_index);


  //정수로 변환 
  int j1_angle=j1_str.toInt();
  int j2_angle=j2_str.toInt();
  int j3_angle=j3_str.toInt();
  int j4_angle=j4_str.toInt();
  int gripper_angle=gripper_str.toInt();


  intArray[0]=j1_angle;
  intArray[1]=j2_angle;
  intArray[2]=j3_angle;
  intArray[3]=j4_angle;
  intArray[4]=gripper_angle;

}



void setup() {
  Serial.begin(115200);
  mySerial.begin(115200);



  base.attach(9);  // attaches the servo on pin 9 to the Servo object
  shoulder1.attach(10);
  shoulder2.attach(11);
  elbow.attach(5);
  wrist.attach(6);
  finger.attach(3);

  

}

void loop() {

    //시리얼 입력까지 대기함
    String receive_from_rasberry = waitUntilAngleInput(mySerial); 
    
    Serial.println(receive_from_rasberry);

    //깨진 명령어가 왔을 경우 invalid라고 보내는 것을 반복하여 올바른 명령어를 받아냄 
    while(!checkSumValidity(receive_from_rasberry)){
        sendInvalidMesg(mySerial);
        String receive_from_rasberry = waitUntilAngleInput(mySerial);
        Serial.println(receive_from_rasberry);
    }

    //명령어 파싱해서 목표각 받아냄
    int* targetAngleArray=parse_abcd_str(receive_from_rasberry);

    //모터 움직임 
    slow_write_to_servo(base,shoulder1,shoulder2,elbow,wrist,finger,targetAngleArray);
    
    //DONE 전송 
    sendDoneMesg(mySerial);

  }





 

