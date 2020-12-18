@Override
protected void onBindDialogView(View view) {
super.onBindDialogView(view);
EditText editText = getEditText();
// Set the selection based on the mSelectionMode
int length = editText.getText() != null ? editText.getText().length() : 0;
if (!TextUtils.isEmpty(editText.getText())) {
switch (mSelectionMode) {
case SELECTION_CURSOR_END:
editText.setSelection(length);
break;
case SELECTION_CURSOR_START:
editText.setSelection(0);
break;
case SELECTION_SELECT_ALL:
editText.setSelection(0, length);
break;
}
}
}
