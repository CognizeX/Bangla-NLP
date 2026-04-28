"""
@Author : Sad Bin Siddique
@Email : sadbinsiddique@gmail.com
"""
import logging
import os
import re
from typing import Optional

import bangla
import soundfile as sf
import torch
from bnnumerizer import numerize
from bnunicodenormalizer import Normalizer

from helper.raw_data import download_file
from helper.synthsizer import Synthesizer

logging.basicConfig(level=logging.INFO)
bnorm = Normalizer()
root_dir = os.getcwd()

DEBUG_SAVE = True

# set pretrain model female or male
DEBUG_GENDER = ["female", "male"]
GENDER = DEBUG_GENDER[0]


def model_loading(model_path=None, config_path=None):
    if not model_path or not config_path:
        model_path, config_path = download_file(root_dir=root_dir, output_path="models", gender=GENDER)
    tts_bn_model = Synthesizer(model_path, config_path, use_cuda=torch.cuda.is_available())
    return tts_bn_model


def normalize(sen):
    _words = [bnorm(word)["normalized"] for word in sen.split()]
    return " ".join([word for word in _words if word is not None])


def bangla_tts(
    model: Optional[Synthesizer] = None,
    text="ন্যাচারাল ল্যাঙ্গুয়েজ প্রসেসিং হলো কৃত্রিম বুদ্ধিমত্তার",
    is_male=True,
    is_e2e_vits=True,
    log_dir="logs/unknown.wav",
):
    if model is None:
        raise ValueError("Model is not loaded. Call model_loading() first.")

    if text[-1] != "।":
        text += "।"

    # english numbers to bangla conversion
    res = re.search("[0-9]", text)
    if res is not None:
        text = bangla.convert_english_digit_to_bangla_digit(text)

    # replace ':' in between two bangla numbers with ' এর '
    pattern = r"[০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯]:[০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯]"
    matches = re.findall(pattern, text)

    for m in matches:
        r = m.replace(":", " এর ")
        text = text.replace(m, r)
    try:
        text = numerize(text)
    except Exception:
        pass

    text = normalize(text)

    sentence_enders = re.compile("[।!?]")
    sentences = sentence_enders.split(str(text))
    audio_list = []

    for i in range(len(sentences)):
        if not sentences[i]:
            continue
        text = sentences[i] + "।"
        audio_list.append(torch.as_tensor(model.tts(text)))
    audio = torch.cat([k for k in audio_list])
    numpy_audio = audio.detach().cpu().numpy()
    return numpy_audio


if __name__ == "__main__":
    text = "গানটির পাণ্ডুলিপি পাওয়া যায়নি।"
    file_name = "output/bangla_tts_v4.wav"

    logging.info("Model Downloading ... ")
    model_path, config_path = download_file(root_dir=root_dir, output_path="models", gender=GENDER)
    logging.info("Done")

    tts_bn_model = model_loading(model_path=model_path, config_path=config_path)
    audio = bangla_tts(model=tts_bn_model, text=text, is_male=False, is_e2e_vits=True)
    logging.info("TTS Generation .... ")

    if DEBUG_SAVE:
        logging.info(f"Saving audio file to {file_name}")
        sf.write(file_name, audio, 22050)
