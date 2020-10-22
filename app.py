from flask import Flask, jsonify, request
import json
from db_connector import DB_TEST
from werkzeug.serving import WSGIRequestHandler
import numpy as np 
import time 
import os 
os.environ['CUDA_VISIBLE_DEVICES']=-1
import tensorflow as tf

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

# initialize inference model
MODEL_FILENAME = 'inference_model.pb'
sess = tf.compat.v1.Session()
print("loading graph")
output_graph = os.path.join(CUR_DIR, MODEL_FILENAME)
graph_def = tf.compat.v1.GraphDef()
with tf.gfile.FastGFile(output_graph,'rb') as fp_pb:
    graph_def.ParseFromString(fp_pb.read())
sess.graph.as_default()
tf.import_graph_def(graph_def, name='')

tf_input = sess.graph.get_tensor_by_name("input:0")
tf_output = sess.graph.get_tensor_by_name("output:0")



app = Flask(__name__)
db = DB_TEST('127.0.0.1', 'db_sensor_data', 'root', 'root')
print(db)

len_seq = 10

def inference_status():
    # status가 NULL인 (아직 상태가 추론되지 않은) 레코드를 모아서 추론 진행
    db_ = DB_TEST('127.0.0.1', 'db_sensor_data', 'root', 'root')
    db_.execute('select * from tbl_sensor5 where status is null')
    result_noinfer = db_.fetchall()
    for i in range(len(result_noinfer)):
        datum_id_ = result_noinfer[i][0]
        sensor_id_ = result_noinfer[i][1]
        # status가 NULL인 레코드의 sensor_id와 id를 가져와서 
        # sensor_id가 동일하고 id가 작은 레코드를 len_seq만큼 가녀와서 input batch를 만든다
        query_ = 'select * from tbl_sensor5 where sensor_id=\"' + sensor_id_ + '\" and id <= ' + str(datum_id_) + ' order by id desc limit ' + str(len_seq) 
        db_.execute(query_)
        records = db_.fetchall()
        print([datum_id_, sensor_id_, len(records)])
        if len(records) == len_seq:
            data = []
            for idx_record in reversed(range(len_seq)):
                data.append(records[idx_record][2:7])
            np_input = np.array(data).reshape(1,len_seq,5)
            # tensorflow inference model을 사용하여 정상확률[0,1]을 추론한다.
            # np_output = np.random.rand()
            np_output = sess.run(tf_output, feed_dict = {tf_input: np_input})
            # 선택된 status가 NULL인 record의 status를 update해준다.
            query__ = 'update tbl_sensor5 set status=' + str(int(3*(1-float(np_output)))) + ' where id=' + str(datum_id_)
            db_.execute(query__)
            db_.commit()
    db_.close()



@app.route("/", methods=['GET','POST'])
def basic():
    ip_address = request.remote_addr
    param1 = request.args.get('power', "-1")
    param2 = request.args.get('audio', "-1")
    param3 = request.args.get('gyro', "-1")
    

    print(param1)
    # print(param1.split(','))
    print(param2)
    # print(param2.split(','))
    print(param3)
    # print(param3.split(','))
    # return_str = 'power: '+param1+', gyro: '+param2+', audio: '+param3
    # print(return_str)

    power = param1.split(',')
    audio = param2.split(',')
    gyro = param3.split(',')
    
    if len(power) == len(audio) and 3*len(power) == len(gyro):
        for i in range(len(power)):
            power_ = float(power[i])
            audio_ = float(audio[i])
            gyro_x = float(gyro[i*3])
            gyro_y = float(gyro[i*3+1])
            gyro_z = float(gyro[i*3+2])

            _query = 'insert into tbl_sensor5 (sensor_id, power, audio, gyro_x, gyro_y, gyro_z) values (%s, %s, %s, %s, %s, %s)'
            db.execute(_query, (ip_address, power_, audio_, gyro_x, gyro_y, gyro_z))
        db.commit()
    tic = time.time()
    inference_status()
    print(time.time()-tic)

    # select data to put in network
    # _query = 'select * from tbl_sensor5 where status is null'
    # db.execute(_query)
    # db.
    # db.close()
    return "OK"

if __name__ == "__main__":
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run( host='0.0.0.0',threaded=True)
    
    
# datetime_ = result_noinfer[i][7]
        # str_timestamp = '\"{}-{}-{} {}:{}:{:.2f}\"'.format(datetime_.year, datetime_.month, datetime_.day, datetime_.hour, datetime_.minute, datetime_.second + datetime_.microsecond/1000000)
        # query_ = 'select * from tbl_sensor5 where sensor_id=\"' + sensor_id_ + '\" and create_time < ' + str_timestamp + ' order by id desc limit ' + str(len_seq) 
        
