import streamlit as st
import json
from PIL import Image
from streamlit_utils import *

st.set_page_config(
    page_title="GLM+SD-based advertising graphic generation assistant",
    layout="wide"
)
st.title('Ad content generation assistant')
st.sidebar.expander('')
st.sidebar.subheader('Parameters')
Diruse = st.sidebar.text("使用指引: \n在Prompt下方输入框输入产品中文描述，\n点击Send按钮，即可生成回复。")
prompt = st.sidebar.text_area('Prompt', help = "Text send to chatGLM")
send = st.sidebar.button("Send", key = "send_prompt", help = "Send text to chatGLM")
Feause = st.sidebar.text("Default: \n广告文案生成\nStable Diffusion: \n广告图配文生成")
mode = st.sidebar.radio("Feature",('Default', 'Stable Diffusion'))
max_length = st.sidebar.slider("Max Length", min_value = 1024, max_value = 8192, value = 2048, step = 1024, help = "Prompt Max Length")
temperature = st.sidebar.slider("Temperature", min_value = 0.10, max_value = 1.00, value = 0.95, step = 0.05)
top_p = st.sidebar.slider("Top_p", min_value = 0.1, max_value = 1.0, value = 0.7, step = 0.1)
input_history = st.sidebar.text_area("History", height = 5, value="[]", help = "The history sended")


if mode == "Default":
    if send:
        if not prompt == "":
            prompt_text = prompt
            
            request = chatglm_json(str(prompt_text), json.loads(input_history), int(max_length), float(top_p), float(temperature))
            request_list = json.loads(request)
            response = request_list.get('response')
            history = request_list.get('history')
            st.markdown("### User: ")
            st.markdown(prompt_text)
            st.markdown('### Copywriting assistant: ')
            st.markdown(response)
            st.sidebar.text('Local History')
            st.sidebar.json(history)


if mode == "Stable Diffusion":
    if send:
        if not prompt == "":
            prompt_text = prompt
            prompt_history = [["我接下来会给你一些作画的指令，你要回复出作画内容及对象，回复对象的广告生成文案，不需要给我参考。”好的“也不需要给我不必要的内容，不要生成重复的内容,直接给我广告生成文案和作画对象，你听懂了吗？","听懂了。请给我一些作画的指令。"]]
            request = chatglm_json(str(f"{prompt_text}"), prompt_history, int(max_length), float(top_p), float(temperature))
            request_list = json.loads(request)
            
            draw_object = request_list.get('response')
            if draw_object[0] == "，" or draw_object[0] == "," or draw_object[0] == "。" or draw_object[0] == ".":
                draw_object = draw_object[1:len(draw_object)]
            if draw_object[-1] == "，" or draw_object[-1] == "," or draw_object[-1] == "。" or draw_object[-1] == ".":
                draw_object = draw_object[0:len(draw_object)-1]
            
            # translate prompt Checkpoints
            
            prompt = str(translate(prompt_text))
            # dobj = ","+str(translate(draw_object))
            # prompt += dobj
        
            prompt += "  ,8k resolution, high quality, highly detailed"
            prompt += ",<lora:add_detail:0.5>，"
            # st.markdown(f"绘画对象：{draw_object}")
            st.caption(f"sd-prompt: {prompt}")

            # todo Add预设negative_prompt
            negative_prompt = "text, word, cropped, low quality, normal quality, username, watermark, signature, blurry, soft, soft line, curved line, sketch, ugly, logo, pixelated, lowres,bad proportions,bad anatomy,bad body,long body,deformed,mutation,poorly drawn face,disfigured,extra arms,extra limb,cross-eyed,bad feet,bad hands,Not suitable for children,Pornography,"
            # test use Embeddings
            negative_prompt += "  ,badhandv4,EasyNegative,EasyNegativeV2,ng_deepnegative_v1_75t," 
            
            stable_diffusion(prompt, negative_prompt)

            st.markdown("### User: ")
            st.markdown(prompt_text)
            st.markdown('### Graphic assistant: ')
            image = Image.open('stable_diffusion.png')
            st.markdown(f'{draw_object}')
            st.image(image, caption=' (Drawing with Stable Diffusion)')
            st.sidebar.text('Local History')
            st.sidebar.json([])


