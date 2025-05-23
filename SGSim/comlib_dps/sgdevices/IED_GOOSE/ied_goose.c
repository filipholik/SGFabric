/*
 * goose_publisher_example.c
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <signal.h>

#include "mms_value.h"
#include "goose_publisher.h"
#include "hal_thread.h"

#include "hal_time.h"


//Generates random number from the defined interval
double generateRandomNumber(double minValue, double maxValue)
{
	srand(time(0)); 
	double rNum = ((double) rand() * (maxValue - minValue)) / (double) RAND_MAX + minValue; 
	//printf("Random number generated: %02f \n", rNum); 
	return rNum; 
}

// has to be executed as root!

//GOOSE 6 - 8 
void gooseFloatPoint68(char* interface)
{
    int i = 0;
    for (i = 0; i < 1; i++) { /* for (i = 0; i < 3; i++)*/
	    LinkedList dataSetValues = LinkedList_create(); 	
	    
	    CommParameters gooseCommParameters;
	    gooseCommParameters.appId = 0x0001;
	    gooseCommParameters.dstAddress[0] = 0x01;
	    gooseCommParameters.dstAddress[1] = 0x0c;
	    gooseCommParameters.dstAddress[2] = 0xcd;
	    gooseCommParameters.dstAddress[3] = 0x01;
	    gooseCommParameters.dstAddress[4] = 0x00;
	    
	    if(i == 0) {
               gooseCommParameters.dstAddress[5] = 0x06;			
		 LinkedList_add(dataSetValues, MmsValue_newFloat(generateRandomNumber(5.001, 5.01))); //0x0840A0392E, 5.00698
		 LinkedList_add(dataSetValues, MmsValue_newBitString(16));
	    }
	    if(i == 1) {
               gooseCommParameters.dstAddress[5] = 0x07;
 		LinkedList_add(dataSetValues, MmsValue_newFloat(0)); //0x0800000000
	    }
	    if(i == 2) {
               gooseCommParameters.dstAddress[5] = 0x08;
		 LinkedList_add(dataSetValues, MmsValue_newFloat(5.72096)); //0x0840B7121D
		LinkedList_add(dataSetValues, MmsValue_newBitString(16));
	    }
	    
	    //gooseCommParameters.vlanId = 0;
	    //gooseCommParameters.vlanPriority = 4;
	    GoosePublisher publisher = GoosePublisher_create(&gooseCommParameters, interface);

	    if (publisher) {
		   char s[60];  
		   sprintf(s, "SIPVI3p1_OperationalValues/LLN0$GO$Control_DataSet_%d", i+3); 
		   GoosePublisher_setGoCbRef(publisher, s);
		   GoosePublisher_setConfRev(publisher, 10001);
		   sprintf(s, "SIPVI3p1_OperationalValues/LLN0$DataSet_%d", i+3); 
		   GoosePublisher_setDataSetRef(publisher, s);
		   sprintf(s, "SIP/VI3p1_OperationalValues/LLN0/Control_DataSet_%d", i+3); 
    		   GoosePublisher_setGoID(publisher, s);
		   GoosePublisher_setTimeAllowedToLive(publisher, 3000); 

           if (GoosePublisher_publish(publisher, dataSetValues) == -1) {
	            printf("Error sending message!\n");
	        }
          }
          GoosePublisher_destroy(publisher);
	   LinkedList_destroyDeep(dataSetValues, (LinkedListValueDeleteFunction) MmsValue_delete);
    }
}

void gooseFloatPoint35(char* interface)
{
    int i = 0;
    for (i = 0; i < 3; i++) { /* for (i = 0; i < 3; i++)*/
	    LinkedList dataSetValues = LinkedList_create(); 	
	    
	    CommParameters gooseCommParameters;
	    gooseCommParameters.appId = 0x0001;
	    gooseCommParameters.dstAddress[0] = 0x01;
	    gooseCommParameters.dstAddress[1] = 0x0c;
	    gooseCommParameters.dstAddress[2] = 0xcd;
	    gooseCommParameters.dstAddress[3] = 0x01;
	    gooseCommParameters.dstAddress[4] = 0x00;
	    
	    if(i == 0) {
               gooseCommParameters.dstAddress[5] = 0x03;		 
	    }
	    if(i == 1) {
               gooseCommParameters.dstAddress[5] = 0x04;
	    }
	    if(i == 2) {
               gooseCommParameters.dstAddress[5] = 0x05;		 
	    }
	    LinkedList_add(dataSetValues, MmsValue_newFloat(0)); //0x0800000000
	    LinkedList_add(dataSetValues, MmsValue_newBitString(16));
	    
	    //gooseCommParameters.vlanId = 0;
	    //gooseCommParameters.vlanPriority = 4;
	    GoosePublisher publisher = GoosePublisher_create(&gooseCommParameters, interface);

	    if (publisher) {
		char s_cb[60];
		char s_data[60];  
		char s_go[60];
		if (i == 0) {
			sprintf(s_cb, "SIPVI3p1_OperationalValues/LLN0$GO$Control_DataSet"); 
			sprintf(s_data, "SIPVI3p1_OperationalValues/LLN0$DataSet"); 
			sprintf(s_go, "SIP/VI3p1_OperationalValues/LLN0/Control_DataSet"); 
		}else {
			sprintf(s_cb, "SIPVI3p1_OperationalValues/LLN0$GO$Control_DataSet_%d", i); 
			sprintf(s_data, "SIPVI3p1_OperationalValues/LLN0$DataSet_%d", i); 
			sprintf(s_go, "SIP/VI3p1_OperationalValues/LLN0/Control_DataSet_%d", i); 
		}
		
		GoosePublisher_setGoCbRef(publisher, s_cb);
		GoosePublisher_setDataSetRef(publisher, s_data);
    		GoosePublisher_setGoID(publisher, s_go);
		GoosePublisher_setConfRev(publisher, 10001);
		GoosePublisher_setTimeAllowedToLive(publisher, 3000); 

           if (GoosePublisher_publish(publisher, dataSetValues) == -1) {
	       printf("Error sending message!\n");
	        }
          }
          GoosePublisher_destroy(publisher);
	   LinkedList_destroyDeep(dataSetValues, (LinkedListValueDeleteFunction) MmsValue_delete);
    }
	
}

void gooseNetlab(char* interface, int stNum, int sqNum, bool data)
{
    LinkedList dataSetValues = LinkedList_create(); 	
	CommParameters gooseCommParameters;
	gooseCommParameters.appId = 0x0001;
	gooseCommParameters.dstAddress[0] = 0x01;
	gooseCommParameters.dstAddress[1] = 0x0c;
	gooseCommParameters.dstAddress[2] = 0xcd;
	gooseCommParameters.dstAddress[3] = 0x01;
	gooseCommParameters.dstAddress[4] = 0x00;
    gooseCommParameters.dstAddress[5] = 0x09;

    LinkedList_add(dataSetValues, MmsValue_newFloat(generateRandomNumber(5.001, 5.01))); 
    LinkedList_add(dataSetValues, MmsValue_newBoolean(data));
    LinkedList_add(dataSetValues, MmsValue_newBitString(0));


    GoosePublisher publisher = GoosePublisher_create(&gooseCommParameters, interface);
	if (publisher) {
		char s_cb[16];
		char s_data[16];  
		char s_go[16];
		sprintf(s_cb, "SIPVI3p1_Operat"); 
		sprintf(s_data, "SIPVI3p1_Operat"); 
		sprintf(s_go, "SIP/VI3p1_Opera"); 
    	GoosePublisher_setGoCbRef(publisher, s_cb);
		GoosePublisher_setDataSetRef(publisher, s_data);
    	GoosePublisher_setGoID(publisher, s_go);
		GoosePublisher_setConfRev(publisher, 10001);
		GoosePublisher_setTimeAllowedToLive(publisher, 3000); 
		GoosePublisher_setStNumSqNum(publisher, stNum, sqNum);
	}

    if (GoosePublisher_publish(publisher, dataSetValues) == -1) {
	    printf("Error sending message!\n");
	}
          
    GoosePublisher_destroy(publisher);
	LinkedList_destroyDeep(dataSetValues, (LinkedListValueDeleteFunction) MmsValue_delete);
} 

void sub_experiment(char* interface)
{
	//Experiment 30s -1s - 60s 
	for(int i = 0; i < 60; i++){
		//Burst operation
		if(i == 30){
			for(int j = 0; j < 100; j++){
				gooseFloatPoint68(interface);
				Thread_sleep(10);
			}
		}	
		gooseFloatPoint68(interface);
		Thread_sleep(1000);
	}
}

void cont_exp(char* interface)
{
	int sqNum = 1;
	int stNum = 666;
	while(true)
	{
		//gooseFloatPoint68(interface);
		gooseNetlab(interface, stNum, sqNum++, false); 
		Thread_sleep(1000);
	}
}

int main(int argc, char** argv)
{
    char* interface;

    if (argc > 1)
       interface = argv[1];
    else
       interface = "eth0";

    printf("Using interface %s\n", interface);

	cont_exp(interface); 

}




