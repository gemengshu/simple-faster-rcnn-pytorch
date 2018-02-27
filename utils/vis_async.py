import visdom
import multiprocessing
import requests
import json
import uuid


class AsyncVisdom(visdom.Visdom):
    pool = multiprocessing.Pool(1)

    def _send(self, msg, endpoint='events'):
        """
        post msg to server using `multiprocessing.Pool.apply_async` so that Visdom won't block training.
        """
        if msg.get('eid', None) is None:
            msg['eid'] = self.env

        if msg.get('win', None) is None:
            msg['win'] = str(uuid.uuid4())

        self.pool.apply_async(requests.post, args=("{0}:{1}/{2}".format(self.server, self.port, endpoint),),
                              kwds={'data': json.dumps(msg)}, callback=self.post_callback)
        return msg['win']

    @staticmethod
    def post_callback(r):
        if not r.ok:
            msg = "Something went wrong on Visdom. Server sent: {}.".format(r.text)
            # raise ValueError(msg)
            print(msg)
