from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photografia_members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 고유 id
    name = db.Column(db.String(100), nullable=False) # 이름
    gender = db.Column(db.String(10), nullable=False) # 성별
    residence = db.Column(db.String(100), nullable=False) # 거주지
    birth_date = db.Column(db.Date, nullable=False) # 생년월일
    join_date = db.Column(db.Date, default=datetime.utcnow, nullable=False) # 모임 가입일
    one_month_status = db.Column(db.String(1), default='X', nullable=False)  # 가입 한 달 여부 O/X
    notice_participation = db.Column(db.String(1), default='X', nullable=False)  # 공지방 참여 여부 O/X
    warnings = db.Column(db.Integer, default=0, nullable=False) # 경고 횟수
    notes = db.Column(db.String(200), default='', nullable=True) # 비고

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'residence': self.residence,
            'birth_date': self.birth_date.strftime('%Y-%m-%d'),
            'join_date': self.join_date.strftime('%Y-%m-%d'),
            'one_month_status': self.one_month_status,
            'notice_participation': self.notice_participation,
            'warnings': self.warnings,
            'notes': self.notes
        }

@app.route('/members', methods=['POST'])
def add_member():
    data = request.json
    try:
        new_member = Member(
            name=data['name'],
            gender=data['gender'],
            residence=data['residence'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d'),
            join_date=datetime.strptime(data['join_date'], '%Y-%m-%d') if 'join_date' in data else datetime.utcnow(),
            notice_participation=data.get('notice_participation', 'X'),
            warnings=data.get('warnings', 0),
            notes=data.get('notes', '')
        )

        if new_member.join_date + timedelta(days=30) <= datetime.utcnow():
            new_member.one_month_status = 'O'

        db.session.add(new_member)
        db.session.commit()

        return jsonify({'message': 'Member added successfully!', 'member': new_member.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.json
    member = Member.query.get_or_404(member_id)

    try:
        member.name = data.get('name', member.name)
        member.gender = data.get('gender', member.gender)
        member.residence = data.get('residence', member.residence)
        if 'birth_date' in data:
            member.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
        if 'join_date' in data:
            member.join_date = datetime.strptime(data['join_date'], '%Y-%m-%d')
        member.notice_participation = data.get('notice_participation', member.notice_participation)
        member.warnings = data.get('warnings', member.warnings)
        member.notes = data.get('notes', member.notes)

        if member.join_date + timedelta(days=30) <= datetime.utcnow():
            member.one_month_status = 'O'
        else:
            member.one_month_status = 'X'

        db.session.commit()

        return jsonify({'message': 'Member updated successfully!', 'member': member.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()    

    app.run(debug=True)
