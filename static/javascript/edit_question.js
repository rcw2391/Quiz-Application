let is_Added = false;

addAnswer = () => {
    if(!document.getElementById('new_answer_div')){
        new_answer_div = document.createElement('div');
        new_answer_div.setAttribute('id', 'new_answer_div');
        document.forms['edit_question_form'].insertBefore(new_answer_div, document.getElementById('submit_button'));

        answer_quantity_label = document.createElement('label');
        answer_quantity_label.setAttribute('for', 'answer_quantity_input');
        answer_quantity_label.innerHTML = 'How many?';

        answer_quantity_input = document.createElement('input');
        answer_quantity_input.setAttribute('type', 'number');
        answer_quantity_input.setAttribute('id', 'answer_quantity_input');
        answer_quantity_input.setAttribute('name', 'answer_quantity_input');
        answer_quantity_input.setAttribute('oninput', 'numberInput()');

        new_answer_div.appendChild(answer_quantity_label);
        new_answer_div.appendChild(answer_quantity_input);
    }
    is_Added = true;
};

removeAddAnswer = () => {
    if(is_Added){
        document.getElementById('new_answer_div').remove();
    }
    is_Added = false;
}

numberInput = () => {
    if(document.getElementById('new_answer_inputs_div')){
        document.getElementById('new_answer_inputs_div').remove();
    }
    input = document.getElementById('answer_quantity_input').value;
    if (input.length > 1) {
        document.getElementById('answer_quantity_input').value = input[1];
        addAnswerInputs(+input[1]);
    } else if (input.length > 0) {
        addAnswerInputs(+input);
    }    
};

addAnswerInputs = (numberOfAnswers) => {
    new_answer_inputs_div = document.createElement('div');
    new_answer_inputs_div.setAttribute('id', 'new_answer_inputs_div');
    document.getElementById('new_answer_div').appendChild(new_answer_inputs_div);
    for (let i = 0; i < numberOfAnswers; i++) {
        
        new_answer_checkbox_label = document.createElement('label');
        new_answer_checkbox_label.setAttribute('for', 'new_answer_checkbox' + i);
        new_answer_checkbox_label.innerHTML = 'Correct:';

        new_answer_checkbox = document.createElement('input');
        new_answer_checkbox.setAttribute('id', 'new_answer_checkbox' + i);
        new_answer_checkbox.setAttribute('type', 'checkbox');
        new_answer_checkbox.setAttribute('name', 'new_answer_checkbox' + i);
        new_answer_checkbox.setAttribute('value', '1');

        new_answer_label = document.createElement('label');
        new_answer_label.setAttribute('for', 'new_answer' + i);
        new_answer_label.innerHTML = 'New Answer #' + (i + 1) + ':';

        new_answer_input = document.createElement('input');
        new_answer_input.setAttribute('id', 'new_answer' + i);
        new_answer_input.setAttribute('type', 'text');
        new_answer_input.setAttribute('name', 'new_answer' + i);

        number_of_answers_input = document.createElement('input');
        number_of_answers_input.setAttribute('type', 'hidden');
        number_of_answers_input.setAttribute('name', 'number_of_new_answers_input');
        number_of_answers_input.setAttribute('value', numberOfAnswers);

        new_answer_inputs_div.appendChild(new_answer_label);
        new_answer_inputs_div.appendChild(new_answer_input);
        new_answer_inputs_div.appendChild(new_answer_checkbox_label);
        new_answer_inputs_div.appendChild(new_answer_checkbox);
        new_answer_inputs_div.appendChild(number_of_answers_input);

        is_Added = true;
    }
};