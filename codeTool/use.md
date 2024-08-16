### Create Instance

Download URL: https://github.com/criyle/go-judge?tab=readme-ov-file

#### Create a Docker instance, which will be automatically removed after termination
'''
sudo docker run -it --rm --privileged --shm-size=256m -p 5050:5050 --name=go-judge criyle/go-judge
'''

'''
sudo docker run -it --privileged --shm-size=256m -p 5050:5050 --name=go-judge criyle/go-judge
'''

#### Execute operations inside a running Docker container
'''
docker exec -it go-judge /bin/bash
'''
#### Restart

'''
sudo docker restart go-judge 
'''

### Usage Instructions
1. Modify the content and test point directory in RunProgramAndTestPostion.py

2. In the CodeTool/ directory, execute the following command:
'''
python -m ExecutiveProgram.TestExample.RunProgramAndTestPostion
'''