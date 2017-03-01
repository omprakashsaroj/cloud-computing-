#OM Prakash Saroj
import boto.ec2.autoscale
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.cloudwatch import MetricAlarm
from boto.ec2.autoscale import ScalingPolicy
import boto.ec2.cloudwatch

ACCESS_KEY = 'AKIAILOB74WPOLGB56BQ'
SECRET_KEY = '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'

REGION="us-west-2"
AMI_ID="ami-3e32f05e"

EC2_KEY_HANDLE="omsaroj"
INSTANCE_TYPE="t1.micro"
SECGROUP_HANDLE="default"

print "Connecting to autoscaling service"

conn=boto.ec2.autoscale.connect_to_region(REGION,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)

print "creating launch configuration"

lc = LaunchConfiguration(name='my-launchs-config', image_id=AMI_ID,
                             key_name=EC2_KEY_HANDLE, instance_type=INSTANCE_TYPE, 
                             security_groups=[SECGROUP_HANDLE,])
                             
conn.create_launch_configuration(lc)

print "creating autoscaling group"

ag = AutoScalingGroup(group_name='my_groups',
                          availability_zones=['us-west-2b'],
                          launch_config=lc, min_size=1, max_size=2,
                          connection=conn)
conn.create_auto_scaling_group(ag)

print "create auto-scaling policies"

scale_up_policy = ScalingPolicy(
            name='scale_up', adjustment_type='ChangeInCapacity',
            as_name='my_groups', scaling_adjustment=1, cooldown=180)
scale_down_policy = ScalingPolicy(
            name='scale_down', adjustment_type='ChangeInCapacity',
            as_name='my_groups', scaling_adjustment=-1, cooldown=180)

conn.create_scaling_policy(scale_up_policy)
conn.create_scaling_policy(scale_down_policy)

scale_up_policy = conn.get_all_policies(
            as_group='my_groups', policy_names=['scale_up'])[0]
scale_down_policy = conn.get_all_policies(
            as_group='my_groups', policy_names=['scale_down'])[0]
            
            
print "Connecting to cloudwatch"

cloudwatch = boto.ec2.cloudwatch.connect_to_region(REGION,aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)

alarm_dimensions = {"AutoScalingGroupName": 'my_groups'}

print "Creating scale-up alarm"

scale_up_alarm = MetricAlarm(
            name='scale_up_on_cpu', namespace='AWS/EC2',
            metric='CPUUtilization', statistic='Average',
            comparison='>', threshold='70',
            period='60', evaluation_periods=2,
            alarm_actions=[scale_up_policy.policy_arn],
            dimensions=alarm_dimensions)
cloudwatch.create_alarm(scale_up_alarm)

print "Creating scale-down alarm"


scale_down_alarm = MetricAlarm(
            name='scale_down_on_cpu', namespace='AWS/EC2',
            metric='CPUUtilization', statistic='Average',
            comparison='<', threshold='40',
            period='60', evaluation_periods=2,
            alarm_actions=[scale_down_policy.policy_arn],
            dimensions=alarm_dimensions)
cloudwatch.create_alarm(scale_down_alarm)

print "Done!"
