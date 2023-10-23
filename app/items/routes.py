from flask import request, jsonify

from app import db
from app.items import bp
from app.models import Items, Images

from flask_jwt_extended import jwt_required, current_user

ITEMS_PER_PAGE = 5


@bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    # Logic xử lý để lấy danh sách các mục
    try:
        page = request.args.get('page', 1, type=int)
        items = Items.query.filter_by(collector_id=current_user.id, is_deleted=0).paginate(page, ITEMS_PER_PAGE, False)
        result = {
            'result': True,
            'items': [item.serialize() for item in items.items],
            'totalItems': items.total
        }
        return jsonify(result), 200
    except Exception as err:
        if not hasattr(err, 'statusCode'):
            err.statusCode = 500
        return jsonify({'error': str(err)}), err.statusCode

# Định nghĩa route để lấy thông tin một mục theo ID
@bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = Items.query.filter_by(collector_id=current_user.id, id=item_id, is_deleted=0).first()
        if item:
            result = {
                'result': True,
                'item': item.serialize()
            }
            return jsonify(result), 200
        else:
            return jsonify({'result': False, 'errorCode': 1}), 404
    except Exception as err:
        if not hasattr(err, 'statusCode'):
            err.statusCode = 500
        return jsonify({'error': str(err)}), err.statusCode

# Route để tạo một mục mới
@bp.route('/items', methods=['POST'])
def create_item():
    try:
        data = request.get_json()
        name = data.get('name')
        ownerType = data.get('ownerType')
        materialId = data.get('materialId')
        original = data.get('original')
        ageId = data.get('ageId')
        itemType = data.get('itemType')
        dimension = data.get('dimension')
        weight = data.get('weight')
        description = data.get('description')
        audio = data.get('audio')
        featureImageUrl = None

        if not name:
            raise ValueError("Tên vật phẩm không được để trống!")

        if 'resultFeatureImage' in data:
            featureImageUrl = data['resultFeatureImage'][0]['key']

        imageUrls = []

        if 'resultsImages' in data:
            for file in data['resultsImages']:
                imageUrls.append(file['key'])

        obj = {
            'name': name,
            'collector_id': request.collector_id,
            'ownerType': ownerType if ownerType is not None else None,
            'materialId': materialId if materialId is not None else None,
            'original': original if original is not None else None,
            'ageId': ageId if ageId is not None else None,
            'itemType': itemType if itemType is not None else None,
            'dimension': dimension if dimension is not None else None,
            'weight': weight if weight is not None else None,
            'description': description if description is not None else None,
            'audio': audio if audio is not None else None,
            'feature_image': featureImageUrl
        }

        if (
            'collected_date' in data and
            data['collected_date'] is not None and
            data['collected_date'] != "null" and
            not isinstance(data['collected_date'], str) and
            not isinstance(data['collected_date'], int)
        ):
            obj['collected_date'] = data['collected_date']

        item = Items(**obj)
        db.session.add(item)
        item = db.session.commit()

        for imageUrl in imageUrls:
            image = Images(item_id=item.id, name=imageUrl)
            db.session.add(image)

        db.session.commit()

        return jsonify({'message': 'Success'}), 201

    except Exception as err:
        if not hasattr(err, 'statusCode'):
            err.statusCode = 500
        return jsonify({'error': str(err)}), err.statusCode

# Định nghĩa route để chỉnh sửa một mục theo ID
@bp.route('/items/<int:item_id>', methods=['PUT'])
def edit_item(item_id):
    try:
        data = request.get_json()
        name = data.get('name')
        ownerType = data.get('ownerType')
        materialId = data.get('materialId')
        original = data.get('original')
        ageId = data.get('ageId')
        itemType = data.get('itemType')
        dimension = data.get('dimension')
        weight = data.get('weight')
        description = data.get('description')
        audio = data.get('audio')
        collected_date = data.get('collected_date')

        item = Items.query.filter_by(collector_id=current_user.id, id=item_id, is_deleted=0).first()
        featureImageUrl = None

        if item is not None:
            if 'featureImageUrl' in data:
                featureImageUrl = data['featureImageUrl']
            elif 'resultFeatureImage' in data:
                featureImageUrl = data['resultFeatureImage'][0]['key']

            imageUrls = []

            if 'resultsImages' in data:
                for file in data['resultsImages']:
                    imageUrls.append(file['key'])

            # Edit data
            item.name = name if name is not None else item.name
            item.ownerType = ownerType if ownerType is not None else item.ownerType
            item.materialId = materialId if materialId is not None else item.materialId
            item.original = original if original is not None else item.original
            item.ageId = ageId if ageId is not None else item.ageId
            item.itemType = itemType if itemType is not None else item.itemType
            item.dimension = dimension if dimension is not None else item.dimension
            item.weight = weight if weight is not None else item.weight
            item.feature_image = featureImageUrl if featureImageUrl is not None else item.feature_image
            item.description = description if description is not None else item.description
            item.audio = audio if audio is not None else item.audio

            if (
                collected_date is not None and
                collected_date != "null" and
                not isinstance(collected_date, str) and
                not isinstance(collected_date, int)
            ):
                item.collected_date = collected_date

            db.session.commit()

            for imageUrl in imageUrls:
                image = Images(item_id=item.item_id, name=imageUrl)
                db.session.add(image)
                db.session.commit()

            return jsonify({'result': True, 'message': 'Updated successfully!'}), 200

        else:
            return jsonify({'result': False, 'errorCode': 1}), 404

    except Exception as err:
        if not hasattr(err, 'statusCode'):
            err.statusCode = 500
        return jsonify({'error': str(err)}), err.statusCode

# Route để xóa một mục theo ID
@bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        item = Items.query.filter_by(collector_id=current_user.id, id=item_id, is_deleted=0).first()

        if item is not None:
            item.is_deleted = 1
            db.session.commit()

            images = Images.query.filter_by(item_id=item.item_id, is_deleted=0).all()

            for image in images:
                image.is_deleted = 1
                db.session.commit()

            return jsonify({'result': True, 'message': 'Delete item successfully!'}), 200

        else:
            return jsonify({'result': False, 'errorCode': 1}), 404

    except Exception as err:
        if not hasattr(err, 'statusCode'):
            err.statusCode = 500
        return jsonify({'error': str(err)}), err.statusCode
