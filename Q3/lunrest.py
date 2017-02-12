#!flask/bin/python
from flask import Flask,jsonify,abort,make_response,request,url_for
from flask_httpauth import HTTPBasicAuth
import threading
lunrest = Flask(__name__)
luns = [
     {
         'id' : 1,
         'name' : u'testlun',
         'initiator' : u'rosyig',
         'target' : u'rosytg',
         'size' : 3
    },
     {
         'id' : 2,
         'name' : u'backup',
         'initiator' : u'rosyig',
         'target' : u'rosytg',
         'size' : 6
    }
]
"""
Authorization
username: admin 
password: changeit
"""
auth = HTTPBasicAuth()
lock = threading.Lock()

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'changeit'
    else:
        return None
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error':'Unauthorized access'}),401)
def make_public_lun(lun):
    """
    Change id to url
    """
    new_lun = {}
    for field in lun:
        if field == 'id':
            new_lun['uri'] = url_for('get_lun', lun_id = lun['id'], _external = True)
        else:
            new_lun[field] = lun[field]
    return new_lun

@lunrest.route('/storage/api/v1.0/luns',methods = ['GET'])
@auth.login_required
def get_luns():
    """
    List all luns details
    example:
    curl -u admin:changeit -i http://localhost:5000/storage/api/v1.0/luns
    """
    return jsonify({'luns': list(map(make_public_lun, luns))})
@lunrest.route('/storage/api/v1.0/luns/<int:lun_id>',methods = ['GET'])
@auth.login_required
def get_lun(lun_id):
    """
    Get one lun details by lun_id
    curl -u admin:changeit -i http://localhost:5000/storage/api/v1.0/luns/2
    """
    lun =list( filter(lambda t : t['id'] == lun_id, luns))
    if len(lun) == 0 :
        abort(404)
    return jsonify({'lun' : make_public_lun(lun[0])})

@lunrest.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error' : 'Not Found'}),404)

@lunrest.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error' : 'Bad Request'}),400)

@lunrest.route('/storage/api/v1.0/luns',methods = ['POST'])
@auth.login_required
def create_lun():
    """
    Create one or multiple luns
    example:
    curl -u admin:changeit -i -H "Content-Type: application/json" -X POST -d '[{"name":"rosytest","size":4},{"name":"rosytest2","size":5}]' http://localhost:5000/storage/api/v1.0/luns
    """
    result=[]
    datas=request.json
    for data in datas:
        if not data or not 'name' in data or not 'size' in data:
            abort(400)
        if data['size'] <=0:
            abort(400)
        lock.acquire()  
        lun ={
                'id' : luns[-1]['id']+1,
                'name' : data['name'],
                'initiator' : data.get('initiator','default'),
                'target' : data.get('target','default'),
                'size' : data['size']
                }
        luns.append(lun)
        result.append(lun)
        lock.release()
    return jsonify({'lun':list(map(make_public_lun,result))}),201

@lunrest.route('/storage/api/v1.0/luns/<int:lun_id>', methods = ['PUT'])
@auth.login_required
def update_lun(lun_id):
    """
    Update lun information
    example:
    curl -u admin:changeit -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/todo/api/v1.0/tasks/2
    """
    lun = list(filter(lambda t : t['id'] == lun_id, luns))
    if len(lun) == 0 :
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name'])is not str:
        abort(400)
    if 'initiator' in request.json and type(request.json['initiator'])is not str:
        abort(400)
    if 'target' in request.json and type(request.json['target'])is not str:
        abort(400)
    if 'size' in request.json and type(request.json['size']) is not int:
        abort(400)
    lock.acquire()
    lun[0]['name'] = request.json.get('name',lun[0]['name'])
    lun[0]['initiator'] = request.json.get('initiator',lun[0]['initiator'])
    lun[0]['target'] = request.json.get('target',lun[0]['target'])
    lun[0]['size'] = request.json.get('size',lun[0]['size'])
    lock.release()
    return jsonify({'lun' : make_public_lun(lun[0])})

@lunrest.route('/storage/api/v1.0/luns/<int:lun_id>', methods = ['DELETE'])
@auth.login_required
def delete_lun(lun_id):
    """
    Delete lun by lun_id
    example:
    curl -u admin:changeit -i -H "Content-Type: application/json" -X DELETE http://localhost:5000/storage/api/v1.0/luns/4
    """
    lun = list(filter(lambda t : t['id'] == lun_id, luns))
    if len(lun) == 0:
        abort(400)
    lock.acquire()
    luns.remove(lun[0])
    lock.release()
    return jsonify({'Delete result': True})
@lunrest.route('/storage/api/v1.0/luns/retrieve/<lun_name>', methods = ['GET'])
@auth.login_required
def retrieve_lun(lun_name):
    """
    retrieve lun size by lun name
    return lun size whose name equal to lun_name
    example:
    curl -u admin:changeit -i http://localhost:5000/storage/api/v1.0/luns/retrieve/backup
    """
    lun = list(filter(lambda t: t['name'] == lun_name, luns))
    if len(lun) == 0:
        abort(400)
    return jsonify({'lun size' : lun[0]['size']})
if __name__  ==  '__main__':
    lunrest.run(debug = True)

