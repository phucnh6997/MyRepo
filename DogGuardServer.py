from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)

# Cấu hình chuỗi kết nối đến cơ sở dữ liệu MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:P@ssw0rdDG123@localhost/dogguard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy(app)

# Định nghĩa mô hình cho bảng account_management
class AccountManagement(db.Model):
    __tablename__ = 'account_management'
    
    id = db.Column(db.String(255), primary_key=True)
    account = db.Column(db.String(255), nullable=False)
    #leader = db.Column(db.String(255))
    type = db.Column(db.String(255))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(50))  # New status column

# Create tài khoản mới bảng account_management
@app.route('/account/create', methods=['POST'])
def create_account():
    try:
        # Lấy dữ liệu JSON từ yêu cầu
        data = request.get_json()

        # Kiểm tra xem các thông tin cần thiết có trong dữ liệu không
        required_fields = ['id', 'account', 'type', 'start_time', 'end_time', 'status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Tạo một đối tượng mới từ dữ liệu
        new_account = AccountManagement(
            id=data['id'],
            account=data['account'],
            type=data['type'],
            start_time=datetime.strptime(data['start_time'], '%H:%M:%S').time(),
            end_time=datetime.strptime(data['end_time'], '%H:%M:%S').time(),
            status=data['status']
        )

        # Thêm bản ghi vào cơ sở dữ liệu và lưu lại
        db.session.add(new_account)
        db.session.commit()

        # Trả về phản hồi thành công
        return jsonify({'message': 'Account created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route để lấy dữ liệu từ bảng account_management theo ID
@app.route('/account/<string:id>', methods=['GET'])
def get_account_by_id(id):
    try:
        # Thực hiện truy vấn để lấy dữ liệu theo ID
        account = AccountManagement.query.get(id)
        
        # Nếu không tìm thấy tài khoản, trả về phản hồi 404
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        current_time = datetime.now(pytz.timezone('Asia/Bangkok')).time()
        status = account.start_time <= current_time <= account.end_time

        result = {
            'status' : "UNLOCK" if status else "LOCK"
        }
        
        # Trả về kết quả
        return jsonify(result), 200
    
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500

# Route để lấy ALL dữ liệu từ bảng account_management theo ID
@app.route('/accounts/all', methods=['GET'])
def get_all_accounts():
    try:
        # Thực hiện truy vấn để lấy tất cả dữ liệu
        accounts = AccountManagement.query.all()
        
        # Nếu không tìm thấy tài khoản nào, trả về phản hồi rỗng
        if not accounts:
            return jsonify([]), 200
        
        # Duyệt qua các tài khoản để kiểm tra trạng thái
        current_time = datetime.now(pytz.timezone('Asia/Bangkok')).time()
        result = []
        
        for account in accounts:
            status = account.start_time <= current_time <= account.end_time
            account_data = {
                'id': account.id,
                'account': account.account,
                'type': account.type,
                'start_time': account.start_time.strftime('%H:%M:%S') if account.start_time else None,
                'end_time': account.end_time.strftime('%H:%M:%S') if account.end_time else None,
                'status': "UNLOCK" if status else "LOCK"
            }
            result.append(account_data)
        
        # Trả về kết quả dưới dạng danh sách JSON
        return jsonify(result), 200
    
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500

# Update thông tin tài khoản theo ID bảng account_management theo ID
@app.route('/account/<string:id>/update', methods=['PUT'])
def update_account(id):
    try:
        data = request.get_json()
        account = AccountManagement.query.get(id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        if 'account' in data:
            account.account = data['account']
        if 'type' in data:
            account.type = data['type']
        if 'start_time' in data:
            account.start_time = datetime.strptime(data['start_time'], '%H:%M:%S').time()
        if 'end_time' in data:
            account.end_time = datetime.strptime(data['end_time'], '%H:%M:%S').time()
        if 'status' in data:
            account.status = data['status']

        db.session.commit()
        return jsonify({'message': 'Account updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route để cập nhật status cho tài khoản theo ID bảng account_management
@app.route('/account/<string:id>/status', methods=['PUT'])
def update_account_status(id):
    try:
        # Truy vấn để lấy tài khoản từ bảng account_management theo ID
        account_entry = AccountManagement.query.get(id)

        # Nếu không tìm thấy tài khoản, trả về phản hồi 404
        if not account_entry:
            return jsonify({'error': 'Account not found'}), 404
        
        # Lấy dữ liệu JSON từ yêu cầu
        data = request.get_json()
        
        # Kiểm tra xem status có trong dữ liệu không
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        # Cập nhật status
        account_entry.status = data['status']
        
        # Lưu thay đổi vào cơ sở dữ liệu
        db.session.commit()
        
        # Trả về kết quả thành công
        return jsonify({'message': 'Status updated successfully'}), 200
    
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500

# Delete tài khoản theo ID bảng account_management
@app.route('/account/<string:id>/delete', methods=['DELETE'])
def delete_account(id):
    try:
        account = AccountManagement.query.get(id)
        if not account:
            return jsonify({'error': 'Account not found'}), 404

        db.session.delete(account)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route để lấy status của tài khoản theo ID bảng account_management
@app.route('/account/<int:id>/get-status', methods=['GET'])
def get_account_status(id):
    try:
        # Truy vấn để lấy tài khoản từ bảng account_management theo ID
        account_entry = AccountManagement.query.get(id)

        # Nếu không tìm thấy tài khoản, trả về phản hồi 404
        if not account_entry:
            return jsonify({'error': 'Account not found'}), 404

        # Lấy status hiện tại của tài khoản
        result = {
            'status': account_entry.status
        }

        # Trả về kết quả
        return jsonify(result), 200
    
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500


########################### Định nghĩa mô hình cho bảng overtime_records ###########################
class OvertimeRecords(db.Model):
    __tablename__ = 'overtime_records'
    
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), nullable=False)
    start_time_ot = db.Column(db.DateTime)  # Changed to DateTime
    end_time_ot = db.Column(db.DateTime)    # Changed to DateTime
    leader = db.Column(db.String(255))
    status = db.Column(db.String(50))
    note = db.Column(db.Text)

# Create row overtime_record mới bảng overtime_record
@app.route('/overtime/create', methods=['POST'])
def create_overtime_record():
    try:
        # Lấy dữ liệu JSON từ yêu cầu
        data = request.get_json()

        # Kiểm tra xem các thông tin cần thiết có trong dữ liệu không
        required_fields = ['account', 'start_time_ot', 'end_time_ot', 'leader', 'status', 'note']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        # Tạo một đối tượng mới từ dữ liệu
        new_overtime_record = OvertimeRecords(
            account=data['account'],
            start_time_ot=datetime.strptime(data['start_time_ot'], '%Y-%m-%d %H:%M:%S'),
            end_time_ot=datetime.strptime(data['end_time_ot'], '%Y-%m-%d %H:%M:%S'),
            leader=data['leader'],
            status=data['status'],
            note=data['note']
        )

        # Thêm bản ghi vào cơ sở dữ liệu và lưu lại
        db.session.add(new_overtime_record)
        db.session.commit()

        # Trả về phản hồi thành công
        return jsonify({'message': 'Overtime record created successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Lấy thông tin bản ghi overtime theo ID
@app.route('/overtime/get/<int:id>', methods=['GET'])
def get_overtime_record(id):
    try:
        # Tìm bản ghi theo ID
        record = OvertimeRecords.query.get(id)
        if not record:
            # Trả về thông báo lỗi nếu không tìm thấy bản ghi
            return jsonify({'error': 'Record not found'}), 404

        # Trả về dữ liệu bản ghi dưới dạng JSON
        return jsonify({
            'id': record.id,
            'account': record.account,
            'start_time_ot': record.start_time_ot.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time_ot': record.end_time_ot.strftime('%Y-%m-%d %H:%M:%S'),
            'leader': record.leader,
            'status': record.status,
            'note': record.note
        }), 200

    except Exception as e:
        # Xử lý ngoại lệ và trả về lỗi
        return jsonify({'error': str(e)}), 500

#Get all data từ bảng overtime_records
@app.route('/overtime_records/all', methods=['GET'])
def get_all_overtime_records():
    try:
        # Thực hiện truy vấn để lấy tất cả dữ liệu từ bảng overtime_records
        overtime_records = OvertimeRecords.query.all()
        
        # Nếu không có bản ghi nào, trả về phản hồi rỗng
        if not overtime_records:
            return jsonify([]), 200
        
        # Duyệt qua các bản ghi và thêm vào kết quả trả về
        result = []
        for record in overtime_records:
            record_data = {
                'id': record.id,
                'account': record.account,
                'start_time_ot': record.start_time_ot.strftime('%Y-%m-%d %H:%M:%S') if record.start_time_ot else None,
                'end_time_ot': record.end_time_ot.strftime('%Y-%m-%d %H:%M:%S') if record.end_time_ot else None,
                'leader': record.leader,
                'status': record.status,
                'note': record.note
            }
            result.append(record_data)
        
        # Trả về kết quả dưới dạng JSON
        return jsonify(result), 200
    
    except Exception as e:
        # Xử lý lỗi và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500

# Route để lấy dữ liệu từ bảng overtime_records theo ID của bảng account_management
@app.route('/overtime/<string:id>', methods=['GET'])
def get_overtime_by_account(id):
    try:
        # Truy vấn để lấy account từ bảng account_management theo ID
        account_entry = AccountManagement.query.get(id)

        # Nếu không tìm thấy tài khoản, trả về phản hồi 404
        if not account_entry:
            return jsonify({'error': 'Account not found'}), 404
        
        account_name = account_entry.account
        
        # Lấy thời gian hiện tại và làm cho nó trở thành timezone-aware
        now = datetime.now(pytz.timezone('Asia/Bangkok'))
        
        # Truy vấn để lấy dữ liệu từ bảng overtime_records theo account
        overtime_records = OvertimeRecords.query.filter(
            OvertimeRecords.account == account_name,
            OvertimeRecords.start_time_ot <= now,
            OvertimeRecords.end_time_ot >= now
        ).all()
        
        # Nếu không tìm thấy bản ghi, trả về phản hồi 200 với trạng thái 'LOCK'
        if not overtime_records:
            return jsonify({'status': 'LOCK'}), 200

        # Nếu có bản ghi, trả về trạng thái 'UNLOCK'
        return jsonify({'status': 'UNLOCK'}), 200
    
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500


# update thông tin bản ghi overtime theo ID
@app.route('/overtime/<int:id>/update', methods=['PUT'])
def update_overtime_record(id):
    try:
        # Tìm bản ghi theo ID
        record = OvertimeRecords.query.get(id)
        if not record:
            # Trả về thông báo lỗi nếu không tìm thấy bản ghi
            return jsonify({'error': 'Record not found'}), 404

        # Lấy dữ liệu JSON từ yêu cầu
        data = request.get_json()

        # Cập nhật các thông tin của bản ghi
        record.start_time_ot = datetime.strptime(data['start_time_ot'], '%Y-%m-%d %H:%M:%S')
        record.end_time_ot = datetime.strptime(data['end_time_ot'], '%Y-%m-%d %H:%M:%S')
        record.leader = data['leader']
        record.status = data['status']
        record.note = data['note']

        # Lưu các thay đổi vào cơ sở dữ liệu
        db.session.commit()
        return jsonify({'message': 'Overtime record updated successfully'}), 200

    except Exception as e:
        # Xử lý ngoại lệ và trả về lỗi
        return jsonify({'error': str(e)}), 500


# Xóa bản ghi overtime theo ID
@app.route('/overtime/<int:id>/delete', methods=['DELETE'])
def delete_overtime_record(id):
    try:
        # Tìm bản ghi theo ID
        record = OvertimeRecords.query.get(id)
        if not record:
            # Trả về thông báo lỗi nếu không tìm thấy bản ghi
            return jsonify({'error': 'Record not found'}), 404

        # Xóa bản ghi khỏi cơ sở dữ liệu
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Overtime record deleted successfully'}), 200

    except Exception as e:
        # Xử lý ngoại lệ và trả về lỗi
        return jsonify({'error': str(e)}), 500

# Chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
