#====== Это моя новая ветка ======
#====== Эксперимент ======

import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import string

load_dotenv()

TOKEN = os.getenv("TOKEN")

#=== Класс, который описывает шаги анкеты ===
#=== Каждая переменная - один шаг ===
class Form(StatesGroup):
# StatesGroup - дает возможность создавать состояния
    name = State()
    age = State()
    city = State()
    hobby = State()
#name и age объекты типа State()
#aiogram использует их как метки для шагов

async def register(dp: Dispatcher):
    @dp.message(Command("start"))
    async def start(message: types.Message, state: FSMContext):
        await message.answer("Привет!\n\nКак тебя зовут?")
        await state.set_state(Form.name)



    #F.text отвечает за прием только текста
    @dp.message(Form.name, F.text)
    async def process_name(message: types.Message, state: FSMContext):

        text = message.text.strip()

         # Проверяем: если в тексте есть цифры — просим ввести имя правильно
         #any - проверяет весь результат
         #Если результат того, что есть цифра в одной из символов текста будет True, то не допустит
        if any(char.isdigit() for char in text):
                await message.answer("❌ Имя не должно содержать цифр! Напиши имя буквами.")
                return
        #return нужен для прерывания цикла, иначе без него будут неверные данные
        #и цикл не сработает
        if any(char in string.punctuation for char in text):
            await message.answer("❌Введите имя буквами!")
            return

        await state.update_data(name=message.text.strip())
        await message.answer(f"Приятно познакомиться, *{message.text}*!\nСколько тебе лет?", parse_mode="Markdown")
        await state.set_state(Form.age)

    #Принимает все кроме текста
    @dp.message(Form.name)
    async def invalid_name(message: types.Message):
        await message.answer("❌Пожалуйста, напишите свое имя текстом!")

    @dp.message(Form.age, F.text)
    async def age(message: types.Message, state: FSMContext):
        age1 = message.text.strip()
        #Проверяет есть ли буквы в строке
        if not age1.isdigit():
            await message.answer("❌Вам нужно ввести возраст цифрами")
            return

        if any(char in string.punctuation for char in age1):
            await message.answer("❌Введите возраст буквами!")
            return


            #Если нет букв, то возвращает число, а не строку
        age2 = int(age1)
        if age2 < 0:
            await message.answer("❌Введите свой реальный возраст (5-120):")
            return
        if age2 > 120:
            await message.answer("❌Введите свой реальный возраст (5-120):")
            return
        await state.update_data(age=age2)
        await message.answer("Из какого ты города?")
        await state.set_state(Form.city)


    #Работает если прислали не текст
    @dp.message(Form.age)
    async def inage(message: types.Message):
        await message.answer("❌Пожалуйста, напиши возраст числом")


    @dp.message(Form.city, F.text)
    async def city(message: types.Message, state: FSMContext):
        text = message.text.strip()
        if any(char.isdigit() for char in text):
            await message.answer("❌Пожалуйста введите название своего города буквами!")
            return
        await state.update_data(city=text)
        await message.answer("Какое твое любимое хобби?")
        await state.set_state(Form.hobby)


    @dp.message(Form.hobby)
    async def hobby(message: types.Message, state: FSMContext):
        text = message.text.strip()
        if any(char.isdigit() for char in text):
            await message.answer("Введите пожалуйста ваши хобби, без цифр")
            return
        await state.update_data(hobby=text)
        # Достает все данные анкеты
        data = await state.get_data()
        name = data.get("name")
        age3 = data.get("age")
        city2 = data.get("city")
        hobby = data.get("hobby")
        await message.answer(
            f"Спасибо за анкету!\n"
            f"Имя: {name}\n"
            f"Возраст: {age3}\n"
            f"Город: {city2}\n"
            f"Хобби: {hobby}\n\n"
            f"✨Анкета завершена, можешь начать заново /start"
            )
        await state.clear()
        # Удаляет все временные файлы

    @dp.message(Command("stop"))
    async def stop1(message: types.Message, state: FSMContext):
        #Проверяет есть ли активное состояние
        currentst = await state.get_state()

        if currentst is None:
            await message.answer("❌Ты не заполняешь анкету")
            return
        await state.clear()
        await message.answer("✅Анкетирование отменено!\nЧтобы начать заново, напиши /start")

    @dp.message()
    async def unknown(message: types.Message, state: FSMContext):
        currentst = await state.get_state()
        if currentst:
            await message.answer("⚠️Сейчас идет анкетирование\nОтветь на вопрос или напиши /stop для отмены")
        else:
            await message.answer("Я не понимаю эту команду, напиши /start")


async def main():
    logging.basicConfig (level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                        )

    bot = Bot(TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    await register(dp)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())





