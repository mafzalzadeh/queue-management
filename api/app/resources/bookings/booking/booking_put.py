'''Copyright 2018 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.'''

import logging
from flask import request, g
from flask_restx import Resource
from qsystem import api, db
from app.models.bookings import Booking, Room, Invigilator
from app.models.theq import CSR
from app.schemas.bookings import BookingSchema
from app.utilities.auth_util import Role, has_any_role
from app.auth.auth import jwt


@api.route("/bookings/<int:id>/", methods=["PUT"])
class BookingPut(Resource):

    booking_schema = BookingSchema()

    @jwt.has_one_of_roles([Role.internal_user.value])
    def put(self, id):

        csr = CSR.find_by_username(g.jwt_oidc_token_info['preferred_username'])

        json_data = request.get_json()
        i_id_list = json_data.get('invigilator_id')

        if not json_data:
            return {"message": "No input data received for updating a ooking"}

        booking = Booking.query.filter_by(booking_id=id).first_or_404()
        booking = self.booking_schema.load(json_data, instance=booking, partial=True)
        warning = self.booking_schema.validate(json_data)

        if warning:
            logging.warning("WARNING: %s", warning)
            return {"message": warning}, 422

        if booking.office_id == csr.office_id or csr.ita2_designate == 1:

            if 'invigilator_id' in json_data:
                booking.invigilators = []

            if type(i_id_list) == int:

                booking.invigilators.append(Invigilator.query.filter_by(invigilator_id=i_id_list).first_or_404())
                db.session.add(booking)
                db.session.commit()

            elif type(i_id_list) == list:

                if len(i_id_list) == 0 or i_id_list == [None]:

                    db.session.add(booking)
                    db.session.commit()

                else:

                    for value in i_id_list:
                        booking.invigilators.append(Invigilator.query.filter_by(invigilator_id=value).first_or_404())
                        db.session.add(booking)
                        db.session.commit()

            elif i_id_list is None:

                db.session.add(booking)
                db.session.commit()

            result = self.booking_schema.dump(booking)

            return {"booking": result,
                    "errors": self.booking_schema.validate(booking)}, 200

        else:
            return {"The Booking Office ID and the CSR Office ID do not match!"}, 403
