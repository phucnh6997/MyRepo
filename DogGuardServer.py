from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

app = Flask(__name__)

# Cấu hình chuỗi kết nối đến cơ sở dữ liệu MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/dogguard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy(app)

# Định nghĩa mô hình cho bảng account_management
class AccountManagement(db.Model):
    __tablename__ = 'account_management'
    
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), nullable=False)
    #leader = db.Column(db.String(255))
    type = db.Column(db.String(255))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(50))  # New status column


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


# Route để cập nhật status cho tài khoản theo ID
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


# Route để lấy status của tài khoản theo ID
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


# Định nghĩa mô hình cho bảng overtime_records
class OvertimeRecords(db.Model):
    __tablename__ = 'overtime_records'
    
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), nullable=False)
    start_time_ot = db.Column(db.DateTime)  # Changed to DateTime
    end_time_ot = db.Column(db.DateTime)    # Changed to DateTime
    leader = db.Column(db.String(255))
    status = db.Column(db.String(50))
    note = db.Column(db.Text)

# Route để lấy dữ liệu từ bảng overtime_records theo ID
@app.route('/overtime/<int:id>', methods=['GET'])
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
        
        # Thực hiện truy vấn để lấy dữ liệu từ bảng overtime_records theo account
        overtime_records = OvertimeRecords.query.filter(
            OvertimeRecords.account == account_name,
            OvertimeRecords.start_time_ot < now,
            OvertimeRecords.end_time_ot > now
        ).all()
        
        # Nếu không tìm thấy bản ghi, trả về phản hồi 404
        if not overtime_records:
            return jsonify({'status': 'LOCK'}), 200

        status = True
        for record in overtime_records:
            # Đảm bảo start_time_ot và end_time_ot là timezone-aware
            if record.start_time_ot.tzinfo is None:
                start_time_ot = record.start_time_ot.replace(tzinfo=pytz.timezone('Asia/Bangkok'))
            else:
                start_time_ot = record.start_time_ot
            
            if record.end_time_ot.tzinfo is None:
                end_time_ot = record.end_time_ot.replace(tzinfo=pytz.timezone('Asia/Bangkok'))
            else:
                end_time_ot = record.end_time_ot
            
            # So sánh với thời gian hiện tại
            status += start_time_ot <= now <= end_time_ot
            result= {
                'status': "UNLOCK" if status else "LOCK"
            }
        
        # Trả về kết quả
        return jsonify(result), 200
    
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi 500
        return jsonify({'error': str(e)}), 500


# Chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
