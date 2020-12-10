# Assumptions
<!-- <h1>Assumptions</h1> -->

[[_TOC_]]
## Assumptions for each functions
<!-- <h2>Functions</h2> -->

### auth.py
<!-- <h3>auth</h3> -->
<table>
    <tr>
        <th>Function</th>
        <th>Assumption(s)</th>
    </tr>
    <tr>
        <td>auth_login</td>
        <td><ul>
            <li>Token will be stored successfully into a dictionary called USER_DATA once users are logged in
            <br/><br/>
            <li>Token is valid (token is a string)
        </ul></td>
    </tr>
    <tr>
        <td>auth_logout</td>
        <td><ul>
            <li>When loging out, the stored token will be removed from the USER_DATA
        </ul></td>
    </tr>
    <tr>
        <td>auth_register</td>
        <td><ul>
            <li>Token is the email for registration of the user
            <br/><br/>
            <li>User's u_id is generated from the increment of members of flockr, in which the initial number is 0
            <br/><br/>
            <li>2 Users can have exactly the same first_name, last_name and password
            <br/><br/>
            <li>The first member of flockr who has an u_id of 0 is the owner of flockr
            <br/><br/>
            <li>The user's handle is generated from the user's first name and last name. It combines the first letter of first name and the entire last name, and the part where exceeds 20 characters will be cut off automatically
            <br/><br/>
            <li>To be unique, the handle will be generated again if a handle has already existed. It will add the user's u_id to the end of the original handle. If the length of new handle exceeds 20, it will cutoff some characters of user's last name to ensure validity
            <br/><br>
            <li>Users will log in to flockr automatically once they register successfully
        </ul></td>
    </tr>
</table>

### channel.py & channels.py
<!-- <h3>channel & channels</h3> -->

<table>
    <tr>
        <th>Function</th>
        <th>Assumption(s)</th>
    </tr>
    <tr>
        <td>channel_invite</td>
        <td><ul>
            <li>Any authorised user of a channel can invite another user to it
            <br/><br/>
            <li> When getting invited, the user's u_id will be added to the channel’s member
        </ul></td>
    </tr>
    <tr>
        <td>channel_details</td>
        <td><ul>
            <li> The member of all_members appears the same order as they joined the channel
            <br/><br/>
            <li> The member of owner_members appears the same order as they became the owner of the channel
        </ul></td>
    </tr>
    <tr>
        <td>channel_messages</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>channel_leave</td>
        <td><ul>
            <li>If the owner of the channel call the channel_leave, he/she will be neither an owner nor a member
            <br/><br/>
            <li>A channel can be empty, which means a member or an owner of a channel can leave it even if she/he is the last person in it
    </tr>
    <tr>
        <td>channel_join</td>
        <td><ul>
            <li>The members of flockr can join in any public channels, while they can only join in a private channel by invitations given by owners or members of that channel
        </ul></td>
    </tr>
    <tr>
        <td>channel_addowner</td>
        <td><ul>
            <li>An authorised user in an existing chanel is an owner of it. Only the authorised user can add owners to that channel. One expception is that the owner of flockr can add herself/himself as an owner as long as she/he is already a member of the channel
            <br/><br/>
            <li>An user outside the channel can also be added as an owner of that channel directly. The new added owner will directly becone a member of this channel as well
            <br/><br/>
            <li>The owner of flockr cannot add owners to a particular channel if she/he is not the member of it
        </ul></td>
    </tr>
    <tr>
        <td>channel_removeowner</td>
        <td><ul>
            <li>Owners can remove other owners
            <br/><br/>
            <li>An owner can remove themselves, even if there are no other owners in the channel
            <br/><br/>
            <li>Once removed, the user is still a member of that channel unless she/he leaves that channel
            <br/><br/>
            <li>If the owner of flockr is not a member of a channel, she/he cannot remove any owners of it
        </ul></td>
    </tr>
    <tr>
        <td>channels_list</td>
        <td><ul>
            <li>It will not raise an error if token is not valid.
            An empty dictionary will be returned in that case
            <br/><br/>
            <li> The returned list of dictionares for channels is the same order as they were created
        </ul></td>
    </tr>
    <tr>
        <td>channels_listall</td>
        <td><ul>
            <li>Provide a list of all the channels within flockr, and no authorisation is required. It will not raise an error if token is not valid and return the correct output(i.e. no need to check token)
            <br/><br/>
            <li> The returned list of dictionares for channels is the same order as they were created
        </ul></td>
    </tr>
    <tr>
        <td>channels_create</td>
        <td><ul>
            <li>Different channels can have a same name
            <br/><br/>
            <li>The id of a channel is generated from the increment numbers of channels
            <br/><br/>
            <li>The user who ceate the channel will become the owner of it automatically
        </ul></td>
    </tr>
</table>

### message
<!-- <h3>message</h3> -->

<table>
    <th>Function</th>
    <th>Assumption(s)</th>
    <tr>
        <td>message_send</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>message_remove</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>message_edit</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
</table>

### user
<!-- <h3>user</h3> -->

<table>
    <th>Function</th>
    <th>Assumption(s)</th>
    <tr>
        <td>user_profile</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>user_profile_setname</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>user_profile_setemail</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>user_profile_sethandle</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>users_all</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
</table>

### other
<!-- <h3>other</h3> -->

<table>
    <th >Function</th>
    <th>Assumption(s)</th>
    <tr>
        <td>clear</td>
        <td><ul>
            <li> Only delete the data that created by auth_register and channels_create (for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>users_all</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
    <tr>
        <td>search</td>
        <td><ul>
            <li>(not for iteration 1)
        </ul></td>
    </tr>
</table>

# Division of Branch
<table>
    <tr>
        <th>Branch</th>
        <th>Work</th>
    </tr>
    <tr>
        <td><ul>iteration1</ul></td>
        <td><ul>
        <li>The main branch gathering all the completed and successfully merged files for work required in iteration 1
        </ul></td>
    </tr>
    <tr>
        <td><ul>iteration1_wendy</ul></td>
        <td><ul>
        <li>Completed data.py
        <br/><br/>
        <li>Finished functions and associated tests for: 
        <br/>channel_addowner<br/>channel_removeowner
        <br/>channels_list<br/>channels_listall<br/>channels_create
        </ul></td>
    </tr>
    <tr>
        <td><ul>iteration1_WeiqangZhuang</ul></td>
        <td><ul>
        <li>Finished functions and associated tests for:
        <br/>auth_login & auth_logout
        <br/>channel_invite<br/>channel_details
        <br/>channel_leave<br/>channel_join
        <br/><br/>
        <li>Completed the clear function in other.py
        </ul></td>
    </tr>
    <tr>
        <td><ul>iteration1_YuhanLiang</ul></td>
        <td><ul>
        <li>Finished the function auth_register
        </ul></td>
    </tr>
    <tr>
        <td><ul>iteration1_assumption</ul></td>
        <td><ul>
        <li>Finished assumptions.md 
        </ul></td>
    </tr>
