# coding=utf-8
from aip import AipSpeech
from audio import MyAudio

class voice_hadel(object):
    '''
        百度云API
        getText(self,filepath):filepath:音频文件路径，返回一个字典包含识别出来的文字
        getAudio(self,text,filename):
    '''

    def __init__(self, api_id, api_key, secert_key):
        '''
        :param api_id:百度语音识别应用ID
        :param api_key:百度语音识别应用KEY
        :param secert_key:百度语音识别Secret Key
        :param filepath:传入需要识别文件的路径
        '''
        self.APP_ID = api_id
        self.API_KEY = api_key
        self.SECRET_KEY = secert_key
        self.aipSpeech = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def get_file_content(self, filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def getText(self, filepath):
        '''
        语音转文字
        :param filepath: 语音文件路径
        :return: 识别出来的文字列表
        {'err_no': 3301, 'err_msg': 'speech quality error.', 'sn': '390527292931509778784'}
        '''
        return self.aipSpeech.asr(self.get_file_content(filepath), 'wav', 16000, {'lan': 'zh', })

    def getAudio(self, text, filename):
        # 文字转语音
        '''
        :param text:需要转换成语音的文字
        :param filename: 生成的文件名
        :return: 音频文件

        '''
        result = self.aipSpeech.synthesis(text, 'zh', 1, {
            'vol': 5,
            'per': 4,
        })
        # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
        if not isinstance(result, dict):
            with open(filename, 'wb') as f:
                f.write(result)


if __name__ == '__main__':
    m = MyAudio()
    m.record('Audio_dir/inaudio.wav')

    br = voice_hadel()
    c = br.getText(filepath='Audio_dir/a.wav')
    print(c)
