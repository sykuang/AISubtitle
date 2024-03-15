#!/usr/bin/env python3

import srt
import json
import os
import litellm
from time import sleep


# BATCHSIZE = 50  # later i may use a token conter instead but this is simpler for now
# LANG = "french"
# MODEL = "gpt-3.5-turbo" if os.getenv("MODEL") is None else os.getenv("MODEL")
# VERBOSE = False


class Translator:
    def __init__(
        self,
        lang="Traditional chinese",
        batchsize=20,
        verbose=True,
    ):
        self.lang = lang
        self.model = os.getenv("MODEL") if os.getenv("MODEL") is not None else "gpt-3.5-turbo"
        self.batchsize = batchsize
        self.verbose = verbose
        self.api_type=os.getenv("API_TYPE") if os.getenv("API_TYPE") is not None else "openai"
        if self.api_type =="azure":
            self.model=f"azure/{self.model}"
        self.prompt = f"""You are a professional translator.
    Translate the text below line by line into {lang}, do not add any content on your own, and aside from translating, do not produce any other text, you will make the most accurate and authentic to the source translation possible.

    these are subtitles, meaning each elements are related and in order, you can use this context to make a better translation.
    you will reply with a json array that only contain the translation."""
        # litellm.set_verbose=True
    def makebatch(self, chunk):
        return [x.content for x in chunk]

    def translate_batch(self, batch, maxretry=5):
        blen = len(batch)
        tbatch = []
        batch = json.dumps(batch, ensure_ascii=False)
        lendiff = 1
        while lendiff != 0 and maxretry > 0:  # TODO add max retry ?
            try:
                _completion = litellm.completion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt},
                        {"role": "user", "content": batch},
                    ],
                )
                tbatch = json.loads(_completion.choices[0].message.content)
            except Exception as e:
                if self.verbose:
                    print(e)
                lendiff = 1
                maxretry -= 1
            else:
                lendiff = len(tbatch) - blen
        return tbatch

    def translate_file(self, subs, maxretry=5):
        total_batch = (len(subs) + self.batchsize - 1) // self.batchsize
        for i in range(0, len(subs), self.batchsize):
            print(f"batch {i//self.batchsize + 1} / {total_batch}")

            chunk = subs[i : i + self.batchsize]
            batch = self.makebatch(chunk)
            batch = self.translate_batch(batch, maxretry)
            if len(batch) != len(chunk):
                print("batch failed")
                for j in range(len(chunk)):
                    ret = self.translate_batch([chunk[j].content], maxretry)
                    if len(ret) > 0:
                        chunk[j].content = ret[0]
            else:
                for j, n in enumerate(batch):
                    chunk[j].content = n

    def translate_srt(self, filename):
        sub = open(filename, errors="ignore").read()
        self.subs = list(srt.parse(sub))
        self.translate_file(self.subs)

    def save(self, output):
        with open(output, "w") as f:
            f.write(srt.compose(self.subs))
